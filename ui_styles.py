#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN UI Styles
Moderné CSS štýly pre ADSUN aplikáciu
"""

def get_main_css():
    """Vráti hlavné CSS štýly"""
    return """
    <style>
    /* Hlavné farby a fonty */
    :root {
        --primary-blue: #4A90E2;
        --secondary-green: #7ED321;
        --background-light: #F8F9FA;
        --text-dark: #2C3E50;
        --border-light: #E1E8ED;
    }
    
    /* Skrytie Streamlit elementov */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stRadio > div { flex-direction: row; gap: 2rem; }
    
    /* Hlavný header */
    .main-header {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(74, 144, 226, 0.3);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    
    .header-stats {
        display: flex;
        gap: 2rem;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    
    .stat-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        opacity: 0.9;
    }
    
    /* Process karty */
    .process-card {
        background: white;
        border: 1px solid var(--border-light);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .process-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
        border-color: var(--primary-blue);
    }
    
    .process-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 0.8rem;
    }
    
    .process-meta {
        display: flex;
        gap: 1.5rem;
        font-size: 0.9rem;
        color: #6C757D;
        margin-bottom: 0.5rem;
    }
    
    .process-tag {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .tag-obchod { background: #E3F2FD; color: #1976D2; }
    .tag-vyroba { background: #F3E5F5; color: #7B1FA2; }
    .tag-hr { background: #E8F5E8; color: #388E3C; }
    .tag-it { background: #FFF3E0; color: #F57C00; }
    .tag-admin { background: #FAFAFA; color: #616161; }
    
    /* Rýchle otázky */
    .quick-questions {
        background: var(--background-light);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    .quick-question-btn {
        background: white;
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        color: var(--text-dark);
    }
    
    .quick-question-btn:hover {
        background: var(--primary-blue);
        color: white;
        border-color: var(--primary-blue);
        transform: translateY(-1px);
    }
    
    /* Chat interface */
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-light);
        max-height: 600px;
        overflow-y: auto;
    }
    
    .chat-message {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 10px;
    }
    
    .chat-question {
        background: #E3F2FD;
        border-left: 4px solid var(--primary-blue);
    }
    
    .chat-answer {
        background: #F8F9FA;
        border-left: 4px solid var(--secondary-green);
    }
    
    .ai-analysis {
        background: linear-gradient(135deg, #E8F5E8 0%, #E3F2FD 100%);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #81C784;
    }
    
    /* Formuláre */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid var(--border-light);
        padding: 0.8rem;
    }
    
    .stButton > button {
        border-radius: 8px;
        border: none;
        padding: 0.8rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="primary"] {
        background: var(--primary-blue);
        color: white;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #357ABD;
        transform: translateY(-1px);
    }
    
    /* Sidebar styling */
    .css-1d391kg { padding: 1rem; }
    
    /* Metriky */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid var(--border-light);
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-blue);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6C757D;
        margin-top: 0.5rem;
    }
    
    /* Responzívnosť */
    @media (max-width: 768px) {
        .header-stats { flex-direction: column; gap: 1rem; }
        .process-meta { flex-direction: column; gap: 0.5rem; }
    }
    </style>
    """ 