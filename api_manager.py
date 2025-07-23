#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN API Manager - Bezpečné ukladanie a správa API kľúčov
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict
import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class APIKeyManager:
    """Manager pre bezpečné ukladanie API kľúčov"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".adsun"
        self.config_file = self.config_dir / "config.json"
        self.env_file = Path(".env")
        self.encrypted_file = self.config_dir / "keys.enc"
        
        # Vytvor config directory ak neexistuje
        self.config_dir.mkdir(exist_ok=True)
    
    def _get_encryption_key(self, password: str) -> bytes:
        """Generuje encryption key z hesla"""
        password_bytes = password.encode()
        salt = b'adsun_salt_2024'  # V produkčnom prostredí by malo byť náhodné
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def save_to_env(self, openai_key: str = None, airtable_key: str = None, airtable_base: str = None):
        """Uloží API kľúče do .env súboru"""
        env_content = []
        
        # Načítaj existujúci obsah .env
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                existing_lines = f.readlines()
            
            # Odstráň staré ADSUN kľúče
            for line in existing_lines:
                if not any(key in line for key in ['OPENAI_API_KEY', 'AIRTABLE_API_KEY', 'AIRTABLE_BASE_ID']):
                    env_content.append(line.strip())
        
        # Pridaj nové kľúče
        if openai_key:
            env_content.append(f"OPENAI_API_KEY={openai_key}")
        if airtable_key:
            env_content.append(f"AIRTABLE_API_KEY={airtable_key}")
        if airtable_base:
            env_content.append(f"AIRTABLE_BASE_ID={airtable_base}")
        
        # Zapíš do súboru
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(env_content) + '\n')
        
        return True
    
    def save_encrypted(self, keys: Dict[str, str], password: str):
        """Uloží API kľúče zašifrované"""
        try:
            key = self._get_encryption_key(password)
            fernet = Fernet(key)
            
            encrypted_data = fernet.encrypt(json.dumps(keys).encode())
            
            with open(self.encrypted_file, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            st.error(f"❌ Chyba šifrovania: {e}")
            return False
    
    def load_encrypted(self, password: str) -> Optional[Dict[str, str]]:
        """Načíta zašifrované API kľúče"""
        try:
            if not self.encrypted_file.exists():
                return None
            
            key = self._get_encryption_key(password)
            fernet = Fernet(key)
            
            with open(self.encrypted_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            keys = json.loads(decrypted_data.decode())
            
            return keys
        except Exception as e:
            st.error(f"❌ Chyba dešifrovania: {e}")
            return None
    
    def save_to_config(self, keys: Dict[str, str]):
        """Uloží API kľúče do lokálneho config súboru (nie bezpečné)"""
        config = {
            'api_keys': keys,
            'saved_at': str(Path().absolute()),
            'warning': 'Tento súbor obsahuje API kľúče. Nezdieľajte ho!'
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Nastav permissions len pre vlastníka
        os.chmod(self.config_file, 0o600)
        return True
    
    def load_from_config(self) -> Optional[Dict[str, str]]:
        """Načíta API kľúče z config súboru"""
        try:
            if not self.config_file.exists():
                return None
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            return config.get('api_keys', {})
        except Exception as e:
            st.error(f"❌ Chyba načítavania config: {e}")
            return None
    
    def load_from_env(self) -> Dict[str, str]:
        """Načíta API kľúče z environment variables a .env súboru"""
        keys = {}
        
        # Najprv skús environment variables
        if os.getenv('OPENAI_API_KEY'):
            keys['openai'] = os.getenv('OPENAI_API_KEY')
        if os.getenv('AIRTABLE_API_KEY'):
            keys['airtable_key'] = os.getenv('AIRTABLE_API_KEY')
        if os.getenv('AIRTABLE_BASE_ID'):
            keys['airtable_base'] = os.getenv('AIRTABLE_BASE_ID')
        
        # Ak nie sú v env, skús .env súbor
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        if key == 'OPENAI_API_KEY':
                            keys['openai'] = value
                        elif key == 'AIRTABLE_API_KEY':
                            keys['airtable_key'] = value
                        elif key == 'AIRTABLE_BASE_ID':
                            keys['airtable_base'] = value
        
        return keys
    
    def delete_stored_keys(self):
        """Vymaže všetky uložené kľúče"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            if self.encrypted_file.exists():
                self.encrypted_file.unlink()
            return True
        except Exception as e:
            st.error(f"❌ Chyba mazania: {e}")
            return False
    
    def get_storage_info(self) -> Dict[str, bool]:
        """Informácie o uložených kľúčoch"""
        return {
            'env_file': self.env_file.exists(),
            'config_file': self.config_file.exists(),
            'encrypted_file': self.encrypted_file.exists(),
            'env_variables': bool(os.getenv('OPENAI_API_KEY') or os.getenv('AIRTABLE_API_KEY'))
        }

def render_api_settings():
    """Render pokročilých nastavení API kľúčov"""
    
    # Inicializácia API managera
    if 'api_manager' not in st.session_state:
        st.session_state.api_manager = APIKeyManager()
    
    api_manager = st.session_state.api_manager
    
    with st.expander("⚙️ Pokročilé nastavenia API kľúčov", expanded=False):
        
        st.markdown("### 💾 Spôsoby ukladania")
        
        # Automatické načítanie uložených kľúčov
        if st.button("🔄 Načítať uložené kľúče"):
            # Priorita: encrypted -> config -> env
            loaded_keys = None
            
            # Skús encrypted najprv
            if api_manager.encrypted_file.exists():
                password = st.text_input("🔒 Heslo pre dešifrovanie:", type="password", key="decrypt_pass")
                if password:
                    loaded_keys = api_manager.load_encrypted(password)
            
            # Ak encrypted zlyhá, skús config
            if not loaded_keys:
                loaded_keys = api_manager.load_from_config()
            
            # Ak config zlyhá, skús env
            if not loaded_keys:
                loaded_keys = api_manager.load_from_env()
            
            if loaded_keys:
                # Nastav session state
                if 'openai' in loaded_keys:
                    st.session_state.openai_api_key = loaded_keys['openai']
                    os.environ['OPENAI_API_KEY'] = loaded_keys['openai']
                if 'airtable_key' in loaded_keys:
                    st.session_state.airtable_api_key = loaded_keys['airtable_key']
                if 'airtable_base' in loaded_keys:
                    st.session_state.airtable_base_id = loaded_keys['airtable_base']
                
                st.success("✅ Kľúče načítané!")
                st.rerun()
            else:
                st.warning("⚠️ Žiadne uložené kľúče nenájdené")
        
        # Aktuálne kľúče
        current_openai = st.session_state.get('openai_api_key', '')
        current_airtable_key = st.session_state.get('airtable_api_key', '')
        current_airtable_base = st.session_state.get('airtable_base_id', '')
        
        if current_openai or current_airtable_key:
            st.markdown("### 💾 Uložiť aktuálne kľúče")
            
            save_method = st.radio(
                "Vyberte spôsob ukladania:",
                [
                    "🔒 Zašifrované (najbezpečnejšie)",
                    "📄 .env súbor (odporúčané)", 
                    "⚠️ Lokálny config (menej bezpečné)"
                ]
            )
            
            keys_to_save = {}
            if current_openai:
                keys_to_save['openai'] = current_openai
            if current_airtable_key:
                keys_to_save['airtable_key'] = current_airtable_key
            if current_airtable_base:
                keys_to_save['airtable_base'] = current_airtable_base
            
            if st.button("💾 Uložiť kľúče"):
                if "Zašifrované" in save_method:
                    password = st.text_input("🔒 Heslo pre šifrovanie:", type="password", key="encrypt_pass")
                    if password:
                        if api_manager.save_encrypted(keys_to_save, password):
                            st.success("✅ Kľúče zašifrované a uložené!")
                
                elif ".env súbor" in save_method:
                    if api_manager.save_to_env(current_openai, current_airtable_key, current_airtable_base):
                        st.success("✅ Kľúče uložené do .env súboru!")
                
                elif "Lokálny config" in save_method:
                    if api_manager.save_to_config(keys_to_save):
                        st.success("✅ Kľúče uložené do lokálneho config!")
        
        # Informácie o uložených kľúčoch
        st.markdown("### 📊 Stav uložených kľúčov")
        storage_info = api_manager.get_storage_info()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔒 Zašifrované", "✅" if storage_info['encrypted_file'] else "❌")
            st.metric("📄 .env súbor", "✅" if storage_info['env_file'] else "❌")
        
        with col2:
            st.metric("⚙️ Config súbor", "✅" if storage_info['config_file'] else "❌")
            st.metric("🌍 Env variables", "✅" if storage_info['env_variables'] else "❌")
        
        # Mazanie uložených kľúčov
        if any(storage_info.values()):
            st.markdown("### 🗑️ Mazanie uložených kľúčov")
            if st.button("🗑️ Vymazať všetky uložené kľúče", type="secondary"):
                if api_manager.delete_stored_keys():
                    st.success("✅ Všetky uložené kľúče vymazané!")
                    st.rerun()
        
        # Bezpečnostné tipy
        st.markdown("""
        ### 🔐 Bezpečnostné tipy:
        
        **🔒 Zašifrované ukladanie:**
        - Najbezpečnejšie
        - Vyžaduje heslo pri každom načítaní
        - Kľúče sú šifrované AES-256
        
        **📄 .env súbor:**
        - Štandardný spôsob pre development
        - Automaticky načítané pri spustení
        - Pridajte `.env` do `.gitignore`
        
        **⚠️ Lokálny config:**
        - Menej bezpečné (nezašifrované)
        - Rýchle a jednoduché
        - Len pre testing
        """)

def get_api_keys() -> Dict[str, str]:
    """Získa API kľúče zo všetkých dostupných zdrojov"""
    api_manager = APIKeyManager()
    
    # Priorita: session state -> encrypted -> config -> env
    keys = {}
    
    # Session state (aktuálne zadané)
    if st.session_state.get('openai_api_key'):
        keys['openai'] = st.session_state.openai_api_key
    if st.session_state.get('airtable_api_key'):
        keys['airtable_key'] = st.session_state.airtable_api_key
    if st.session_state.get('airtable_base_id'):
        keys['airtable_base'] = st.session_state.airtable_base_id
    
    # Ak nie sú v session state, skús uložené
    if not keys:
        # Skús config
        stored_keys = api_manager.load_from_config()
        if stored_keys:
            keys.update(stored_keys)
        
        # Skús env
        if not keys:
            env_keys = api_manager.load_from_env()
            keys.update(env_keys)
    
    return keys 