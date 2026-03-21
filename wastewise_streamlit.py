"""
WasteWise Streamlit App - With FiftyOne Analytics
Single-file waste classification app with leaderboard, badges, and FiftyOne insights
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import base64
from PIL import Image
import io
import requests
from anthropic import Anthropic
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

# Load environment variables
load_dotenv()

# ============================================
# FIFTYONE INTEGRATION (ANALYTICS)
# ============================================

def init_fiftyone_dataset():
    """Initialize FiftyOne dataset for analytics"""
    try:
        import fiftyone as fo
        
        # Check if dataset exists
        if "WasteWise_Submissions" in fo.list_datasets():
            return fo.load_dataset("WasteWise_Submissions")
        
        # Create new dataset
        dataset = fo.Dataset("WasteWise_Submissions")
        return dataset
    except Exception as e:
        st.warning(f"FiftyOne not fully initialized: {str(e)}")
        return None

def add_submission_to_fiftyone(image_base64, item_name, bin_type, confidence, city, username):
    """Add user submission to FiftyOne dataset"""
    try:
        import fiftyone as fo
        from fiftyone import ViewFrame
        
        dataset = init_fiftyone_dataset()
        if dataset is None:
            return False
        
        # Decode image
        image_data = base64.b64decode(image_base64)
        image_path = f"/tmp/wastewise_{datetime.now().timestamp()}.jpg"
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        # Add to FiftyOne
        sample = fo.Sample(filepath=image_path)
        sample['item'] = item_name
        sample['bin_type'] = bin_type
        sample['confidence'] = confidence
        sample['city'] = city
        sample['username'] = username
        sample['timestamp'] = datetime.now().isoformat()
        sample['verified'] = False
        
        dataset.add_sample(sample)
        dataset.save()
        return True
    except Exception as e:
        print(f"FiftyOne add error: {e}")
        return False

def get_analytics_data():
    """Get analytics from submissions"""
    data = load_data()
    
    submissions = []
    for username, user in data["users"].items():
        if "submissions" in user:
            for sub in user["submissions"]:
                submissions.append({
                    "username": username,
                    "city": user["city"],
                    "item": sub.get("item", "Unknown"),
                    "bin": sub.get("bin", "Unknown"),
                    "confidence": sub.get("confidence", 0),
                    "timestamp": sub.get("timestamp", ""),
                    "verified": sub.get("verified", False)
                })
    
    return pd.DataFrame(submissions) if submissions else pd.DataFrame()

def get_city_statistics(city):
    """Get waste statistics for a specific city"""
    df = get_analytics_data()
    
    if df.empty or len(df[df['city'] == city]) == 0:
        return None
    
    city_df = df[df['city'] == city]
    
    stats = {
        "total_submissions": len(city_df),
        "recycling_count": len(city_df[city_df['bin'] == 'recycling']),
        "compost_count": len(city_df[city_df['bin'] == 'compost']),
        "landfill_count": len(city_df[city_df['bin'] == 'landfill']),
        "special_count": len(city_df[city_df['bin'] == 'special']),
        "avg_confidence": city_df['confidence'].mean(),
        "common_items": city_df['item'].value_counts().head(5).to_dict(),
        "verified_rate": len(city_df[city_df['verified'] == True]) / len(city_df) * 100 if len(city_df) > 0 else 0
    }
    
    return stats

# ============================================
# PAGE CONFIG
# ============================================

# ============================================
# PAGE CONFIG & STYLING
# ============================================

st.set_page_config(
    page_title="WasteWise",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for green and white theme
st.markdown("""
<style>
    /* Color palette - green and white */
    :root {
        --primary: #1B4332;
        --primary-light: #2D6A4F;
        --primary-lighter: #40916C;
        --accent: #52B788;
        --accent-light: #74C69D;
        --text-dark: #1B4332;
        --text-light: #555555;
        --bg-white: #ffffff;
        --bg-light: #f0f7f4;
        --border: #d4e8e0;
        --border-light: #e8f5f0;
    }
    
    /* Main background */
    body, .stApp {
        background-color: #f0f7f4;
    }
    
    /* Metrics */
    .stMetric {
        background: #ffffff;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #d4e8e0;
        box-shadow: 0 1px 3px rgba(27,67,50,0.05);
    }
    
    .stMetric label {
        color: #555555 !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="metric-container"] {
        color: #1B4332 !important;
    }
    
    .metric-value {
        color: #1B4332 !important;
    }
    
    /* Header styling */
    .header-title {
        font-size: 2.5em;
        font-weight: 600;
        color: #1B4332;
        margin: 0;
        padding: 15px 0;
    }
    
    .header-subtitle {
        font-size: 1em;
        color: #2D6A4F;
        margin: 5px 0;
        font-weight: 400;
    }
    
    /* Cards */
    .card {
        background: #ffffff;
        border-radius: 6px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(27,67,50,0.05);
        margin: 10px 0;
        border: 1px solid #d4e8e0;
    }
    
    /* Buttons */
    .stButton > button {
        background: #2D6A4F;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(27,67,50,0.12);
    }
    
    .stButton > button:hover {
        background: #1B4332;
        box-shadow: 0 2px 4px rgba(27,67,50,0.15);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        background: #e8f5f0;
        color: #1B4332;
        padding: 6px 12px;
        border-radius: 12px;
        font-weight: 500;
        margin: 3px;
        font-size: 0.9em;
        border: 1px solid #d4e8e0;
    }
    
    /* Leaderboard styling */
    .leaderboard-item {
        background: #ffffff;
        padding: 12px;
        border-radius: 6px;
        margin: 8px 0;
        border: 1px solid #d4e8e0;
        border-left: 3px solid #2D6A4F;
    }
    
    /* Stats boxes */
    .stat-box {
        background: #ffffff;
        border-left: 3px solid #2D6A4F;
        padding: 12px;
        border-radius: 6px;
        margin: 8px 0;
        border-top: 1px solid #d4e8e0;
        border-right: 1px solid #d4e8e0;
        border-bottom: 1px solid #d4e8e0;
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stPasswordInput > div > div > input {
        border-radius: 4px;
        border: 1px solid #d4e8e0;
        padding: 8px 10px;
        font-size: 0.95em;
        color: #1B4332;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stPasswordInput > div > div > input:focus {
        border-color: #2D6A4F !important;
        box-shadow: 0 0 0 2px rgba(45,106,79,0.1) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #d4e8e0;
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 4px;
        border: 1px solid #d4e8e0;
    }
    
    /* Global text color */
    p, span, div, h1, h2, h3, h4, h5, h6, label {
        color: #1B4332 !important;
    }
    
    .stMarkdown, .stMarkdown p {
        color: #1B4332 !important;
    }
    
    .stText {
        color: #1B4332 !important;
    }
    
    [data-baseweb="input"] input {
        color: #1B4332 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA STORAGE (JSON-based)
# ============================================

DATA_FILE = "wastewise_data.json"

def load_data():
    """Load user data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "users": {},
        "leaderboard": [],
        "waste_items": {}
    }

def save_data(data):
    """Save user data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ============================================
# AUTHENTICATION
# ============================================

def init_user_session():
    """Initialize user session in Streamlit"""
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_city" not in st.session_state:
        st.session_state.user_city = None

def register_user(username, city):
    """Register new user"""
    data = load_data()
    
    if username in data["users"]:
        return False, "Username already exists"
    
    data["users"][username] = {
        "city": city,
        "totalPoints": 0,
        "totalItemsSorted": 0,
        "currentStreak": 0,
        "longestStreak": 0,
        "joinedAt": datetime.now().isoformat(),
        "stats": {
            "co2Saved": 0.0,
            "waterSaved": 0.0,
            "treesSaved": 0.0
        },
        "badges": [],
        "lastActivityDate": None,
        "submissions": []  # Track submissions for FiftyOne
    }
    
    # Add to leaderboard
    data["leaderboard"].append({
        "username": username,
        "city": city,
        "totalPoints": 0,
        "totalItemsSorted": 0,
        "badges": []
    })
    
    save_data(data)
    return True, "Registration successful!"

def login_user(username):
    """Login user"""
    data = load_data()
    
    if username not in data["users"]:
        return False, "Username not found"
    
    user = data["users"][username]
    return True, user

# ============================================
# WASTE CLASSIFICATION (Claude API)
# ============================================

def classify_waste(image_base64, city: str, media_type: str = "image/jpeg"):
    """Classify waste using Claude Sonnet 4.6"""
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            st.error("⚠️ API key not found. Create a .env file with ANTHROPIC_API_KEY")
            return None
        
        client = Anthropic(api_key=api_key)
        
        system_prompt = f"""You are WasteWise, a waste disposal expert for {city}.
Key rules for Tempe/Phoenix AZ: curbside recycling YES, curbside composting NO, hazardous waste needs special drop-off at city HHW facilities. Pizza boxes go in recycling ONLY if not heavily soiled. Plastic bags go to store drop-off, NOT curbside recycling.
Respond ONLY in valid JSON with no markdown backticks:
{{
  'item': 'short item name (max 4 words)',
  'bin': 'recycling' or 'compost' or 'landfill' or 'special',
  'confidence': float between 0.0 and 1.0,
  'reason': 'one clear sentence explaining why',
  'prep': 'one sentence on what to do before disposing',
  'impact': 'one sentence on environmental impact of correct disposal'
}}"""
        
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=system_prompt,
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': media_type,
                                'data': image_base64
                            }
                        },
                        {
                            'type': 'text',
                            'text': 'Classify this waste item and tell me how to dispose of it properly.'
                        }
                    ]
                }
            ]
        )
        
        response_text = message.content[0].text
        
        # Strip markdown code fences
        if "```" in response_text:
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        result = json.loads(response_text)
        
        # Calculate points and impact
        base_points = {
            "recycling": 100,
            "compost": 120,
            "landfill": 25,
            "special": 150,
        }
        
        result["points"] = int((base_points.get(result["bin"], 50)) * result["confidence"])
        result["environmentalImpact"] = {
            "co2": 2.5 if result["bin"] == "recycling" else (0.5 if result["bin"] == "compost" else 0.1),
            "water": 5 if result["bin"] == "recycling" else (2 if result["bin"] == "compost" else 0.5),
            "trees": 0.001 if result["bin"] == "recycling" else (0.005 if result["bin"] == "compost" else 0)
        }
        
        return result
    
    except Exception as e:
        st.error(f"Classification error: {str(e)}")
        return None

# ============================================
# POINTS & BADGES
# ============================================

def calculate_points(bin_type: str, confidence: float):
    """Calculate points based on bin type and confidence"""
    base_points = {
        "recycling": 100,
        "compost": 120,
        "landfill": 25,
        "special": 150,
    }
    return int((base_points.get(bin_type, 50)) * confidence)

def check_badges(username: str):
    """Check and award badges"""
    data = load_data()
    user = data["users"][username]
    
    badges_to_check = [
        {"id": "first_sort", "condition": user["totalItemsSorted"] == 1, "name": "🎖️ First Step"},
        {"id": "quick_starter", "condition": user["totalItemsSorted"] == 10, "name": "🎖️ Quick Starter"},
        {"id": "eco_warrior", "condition": user["totalItemsSorted"] == 50, "name": "🎖️ Eco Warrior"},
        {"id": "legendary_sorter", "condition": user["totalItemsSorted"] == 100, "name": "🎖️ Legendary Sorter"},
        {"id": "week_streak", "condition": user["longestStreak"] >= 7, "name": "🔥 7-Day Streak"},
        {"id": "month_streak", "condition": user["longestStreak"] >= 30, "name": "🔥 30-Day Legend"},
    ]
    
    current_badges = [b["id"] for b in user["badges"]]
    
    for badge in badges_to_check:
        if badge["condition"] and badge["id"] not in current_badges:
            user["badges"].append({"id": badge["id"], "name": badge["name"]})
            st.success(f"🎉 Unlocked badge: {badge['name']}")
    
    save_data(data)
    return user["badges"]

def update_streak(username: str):
    """Update user streak"""
    data = load_data()
    user = data["users"][username]
    today = datetime.now().date().isoformat()
    
    if user["lastActivityDate"] is None:
        user["currentStreak"] = 1
    elif user["lastActivityDate"] == today:
        pass  # Same day, no change
    else:
        import datetime as dt
        last_date = datetime.fromisoformat(user["lastActivityDate"]).date()
        current_date = datetime.now().date()
        days_diff = (current_date - last_date).days
        
        if days_diff == 1:
            user["currentStreak"] += 1
            user["longestStreak"] = max(user["currentStreak"], user["longestStreak"])
        else:
            user["currentStreak"] = 1
    
    user["lastActivityDate"] = today
    save_data(data)

# ============================================
# UI PAGES
# ============================================

def page_login():
    """Login/Register page - green and white theme"""
    # Initialize session state for showing registration
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    
    # Centered header
    st.markdown("""
    <div style="text-align: center; padding: 40px 0 60px 0;">
        <h1 style="color: #1B4332; font-size: 2.5em; margin: 0; font-weight: 600;">♻️ WasteWise</h1>
        <p style="color: #2D6A4F; font-size: 1em; margin: 10px 0 5px 0; font-weight: 400;">
            Sort Waste. Earn Points. Save the Planet.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.show_register:
            # LOGIN FORM
            st.markdown("""
            <div style="background: #ffffff; padding: 30px; border-radius: 6px; 
                        border: 1px solid #d4e8e0; box-shadow: 0 1px 3px rgba(27,67,50,0.05);">
                <h2 style="color: #1B4332; text-align: center; margin-top: 0;">Login to Your Account</h2>
            </div>
            """, unsafe_allow_html=True)
            
            username = st.text_input("Username", placeholder="Enter your username", key="login_username")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Login", use_container_width=True, key="login_btn"):
                    if username.strip():
                        success, result = login_user(username)
                        if success:
                            st.session_state.username = username
                            st.session_state.user_city = result["city"]
                            st.success("✅ Logged in successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result}")
                    else:
                        st.error("❌ Please enter a username")
            
            with col_b:
                if st.button("Cancel", use_container_width=True, key="cancel_btn"):
                    pass
            
            # Registration link at the bottom
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("<div style='text-align: right; padding-right: 10px;'>Don't have an account?</div>", unsafe_allow_html=True)
            with col2:
                if st.button("Sign up here", key="signup_link", help="Create a new account"):
                    st.session_state.show_register = True
                    st.rerun()
        
        else:
            # REGISTRATION FORM
            st.markdown("""
            <div style="background: #ffffff; padding: 30px; border-radius: 6px; 
                        border: 1px solid #d4e8e0; box-shadow: 0 1px 3px rgba(27,67,50,0.05);">
                <h2 style="color: #1B4332; text-align: center; margin-top: 0;">Create Account</h2>
            </div>
            """, unsafe_allow_html=True)
            
            reg_username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
            city = st.selectbox("City", ["Tempe, AZ", "Phoenix, AZ", "Mesa, AZ", "Other"], key="city_select")
            
            col_c, col_d = st.columns(2)
            with col_c:
                if st.button("Create Account", use_container_width=True, key="register_btn"):
                    if reg_username.strip():
                        success, message = register_user(reg_username, city)
                        if success:
                            st.session_state.username = reg_username
                            st.session_state.user_city = city
                            st.success("✅ Account created! Logging in...")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Please enter a username")
            
            with col_d:
                if st.button("Back", use_container_width=True, key="back_btn"):
                    st.session_state.show_register = False
                    st.rerun()
            
            # Back to login link
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("<div style='text-align: right; padding-right: 10px;'>Already have an account?</div>", unsafe_allow_html=True)
            with col2:
                if st.button("Login", key="login_link", help="Go back to login"):
                    st.session_state.show_register = False
                    st.rerun()


def page_dashboard():
    """User dashboard"""
    data = load_data()
    user = data["users"][st.session_state.username]
    
    # Header
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #1B4332; font-size: 2em; margin: 0;">📊 Welcome Back, {st.session_state.username}</h1>
        <p style="color: #2D6A4F; font-size: 0.95em; margin: 8px 0 0 0;">📍 {st.session_state.user_city}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main stats - 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("⭐ Total Points", user['totalPoints'])
    
    with col2:
        st.metric("♻️ Items Sorted", user['totalItemsSorted'])
    
    with col3:
        st.metric("🔥 Current Streak", f"{user['currentStreak']} days")
    
    with col4:
        st.metric("🏆 Badges", len(user['badges']))
    
    # Environmental Impact Section
    st.markdown("---")
    st.markdown("<h2 style='color: #1B4332; text-align: center;'>🌍 Your Environmental Impact</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🌍 CO₂ Avoided", f"{user['stats']['co2Saved']:.2f} kg")
    
    with col2:
        st.metric("💧 Water Saved", f"{user['stats']['waterSaved']:.1f} L")
    
    with col3:
        st.metric("🌳 Trees Saved", f"{user['stats']['treesSaved']:.3f}")
    
    # Badges Section
    if user["badges"]:
        st.markdown("---")
        st.markdown("<h2 style='color: #1B4332; text-align: center;'>🏆 Your Achievements</h2>", unsafe_allow_html=True)
        
        badge_cols = st.columns(min(len(user["badges"]), 6))
        for i, badge in enumerate(user["badges"]):
            with badge_cols[i % len(badge_cols)]:
                st.markdown(f"""
                <div style="background: #f0f7f4; padding: 15px; border-radius: 6px; 
                            text-align: center; border: 1px solid #d4e8e0;">
                    <p style="font-size: 2em; margin: 0;">🎖️</p>
                    <p style="color: #1B4332; margin: 10px 0 0 0; font-weight: 600; font-size: 0.9em;">{badge['name']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Detailed Findings Section
    if user.get("submissions") and len(user["submissions"]) > 0:
        st.markdown("---")
        st.markdown("<h2 style='color: #1B4332; text-align: center;'>📊 Your Sorting Findings</h2>", unsafe_allow_html=True)
        
        # Breakdown by bin type
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("♻️ Waste Distribution")
            bin_counts = {}
            for sub in user["submissions"]:
                bin_type = sub.get("bin", "unknown")
                bin_counts[bin_type] = bin_counts.get(bin_type, 0) + 1
            
            # Display as metrics
            for bin_type, count in sorted(bin_counts.items()):
                emoji = {"recycling": "♻️", "compost": "🌱", "landfill": "🗑️", "special": "⚠️"}.get(bin_type, "📦")
                st.metric(f"{emoji} {bin_type.title()}", count)
        
        with col2:
            st.subheader("🎯 Classification Quality")
            # Average confidence
            confidences = [sub.get("confidence", 0) for sub in user["submissions"]]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("📈 Avg Confidence", f"{avg_confidence:.0%}")
            with col_b:
                verified = len([s for s in user["submissions"] if s.get("verified", False)])
                st.metric("✅ Verified Items", f"{verified}/{len(user['submissions'])}")
        
        # Recent classifications
        st.subheader("📝 Recent Classifications")
        submissions_sorted = sorted(user["submissions"], key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        
        for i, sub in enumerate(submissions_sorted):
            bin_emoji = {"recycling": "♻️", "compost": "🌱", "landfill": "🗑️", "special": "⚠️"}.get(sub.get("bin", ""), "📦")
            verified_badge = "✅" if sub.get("verified") else "⏳"
            time_str = sub.get("timestamp", "").split("T")[0] if sub.get("timestamp") else "N/A"
            
            st.markdown(f"""
            <div style="background: #f0f7f4; padding: 12px; border-radius: 6px; margin: 8px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #1B4332;">📦 {sub.get('item', 'Unknown')}</strong>
                        <span style="color: #2D6A4F; margin-left: 10px;">{bin_emoji} {sub.get('bin', 'unknown').title()}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #2D6A4F; font-weight: 600;">{sub.get('confidence', 0):.0%}</span>
                        <span style="color: #555555; margin-left: 10px; font-size: 0.9em;">{verified_badge} {time_str}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def page_sort():
    """Waste sorting page"""
    st.markdown("# ♻️ Sort Your Waste")
    st.markdown("Take a photo with your camera or upload an image to classify waste")
    
    # Two options: camera or upload
    col1, col2 = st.columns(2)
    
    captured_image = None
    uploaded_image = None
    
    with col1:
        st.subheader("📷 Take a Photo")
        captured_image = st.camera_input("Use your phone camera")
    
    with col2:
        st.subheader("📁 Upload Image")
        uploaded_image = st.file_uploader("Or upload from gallery", type=["jpg", "jpeg", "png", "webp"])
    
    # Use whichever was provided
    image_data = captured_image if captured_image is not None else uploaded_image
    
    if image_data is not None:
        # Display image
        image = Image.open(image_data)
        st.image(image, caption="Waste item", use_column_width=True)
        
        # Classify
        if st.button("🔍 Analyze Waste", use_container_width=True):
            with st.spinner("Analyzing with Claude AI..."):
                # Convert to base64
                image_bytes = image_data.getvalue()
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                
                # Determine media type
                media_type_map = {
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "png": "image/png",
                    "webp": "image/webp"
                }
                # Get file extension for uploaded files, camera is always JPEG
                if hasattr(image_data, 'name'):
                    suffix = image_data.name.split('.')[-1].lower()
                    media_type = media_type_map.get(suffix, "image/jpeg")
                else:
                    media_type = "image/jpeg"  # Camera input is always JPEG
                
                # Classify
                result = classify_waste(base64_image, st.session_state.user_city, media_type)
                
                if result:
                    # Display result
                    st.success("✅ Classification Complete!")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📦 Item", result['item'])
                    
                    with col2:
                        bin_emoji = {"recycling": "♻️", "compost": "🌱", "landfill": "🗑️", "special": "⚠️"}.get(result["bin"], "")
                        st.metric("🗑️ Bin", f"{bin_emoji} {result['bin'].title()}")
                    
                    with col3:
                        confidence_pct = result['confidence']*100
                        st.metric("🎯 Confidence", f"{confidence_pct:.0f}%")
                    
                    with col4:
                        st.metric("⭐ Points", f"+{result['points']}")
                    
                    st.markdown("---")
                    
                    # Details with clean styling
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: #f0f7f4; padding: 15px; border-radius: 6px; 
                                    border-left: 3px solid #2D6A4F;">
                            <h4 style="color: #1B4332; margin-top: 0;">💡 Why This Bin?</h4>
                            <p style="color: #555555; margin: 0; font-size: 0.95em;">{result['reason']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style="background: #f0f7f4; padding: 15px; border-radius: 6px; 
                                    border-left: 3px solid #2D6A4F; margin-top: 10px;">
                            <h4 style="color: #1B4332; margin-top: 0;">🌍 Environmental Impact</h4>
                            <p style="color: #555555; margin: 0; font-size: 0.95em;">{result['impact']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="background: #f0f7f4; padding: 15px; border-radius: 6px; 
                                    border-left: 3px solid #2D6A4F;">
                            <h4 style="color: #1B4332; margin-top: 0;">📋 How to Prepare</h4>
                            <p style="color: #555555; margin: 0; font-size: 0.95em;">{result['prep']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style="background: #f0f7f4; padding: 15px; border-radius: 6px; 
                                    border-left: 3px solid #2D6A4F; margin-top: 10px;">
                            <h4 style="color: #1B4332; margin-top: 0;">📊 Your Savings</h4>
                            <p style="color: #555555; margin: 5px 0; font-size: 0.9em;">🌍 CO₂: -{result['environmentalImpact']['co2']:.2f}kg</p>
                            <p style="color: #555555; margin: 5px 0; font-size: 0.9em;">💧 Water: -{result['environmentalImpact']['water']:.1f}L</p>
                            <p style="color: #555555; margin: 5px 0; font-size: 0.9em;">🌳 Trees: +{result['environmentalImpact']['trees']:.4f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Save this classification
                    if st.button("✅ Save & Earn Points", use_container_width=True):
                        data = load_data()
                        user = data["users"][st.session_state.username]
                        
                        # Update user stats
                        user["totalPoints"] += result["points"]
                        user["totalItemsSorted"] += 1
                        user["stats"]["co2Saved"] += result["environmentalImpact"]["co2"]
                        user["stats"]["waterSaved"] += result["environmentalImpact"]["water"]
                        user["stats"]["treesSaved"] += result["environmentalImpact"]["trees"]
                        
                        # Store submission for FiftyOne analysis
                        submission = {
                            "timestamp": datetime.now().isoformat(),
                            "item": result["item"],
                            "bin": result["bin"],
                            "confidence": result["confidence"],
                            "verified": False
                        }
                        if "submissions" not in user:
                            user["submissions"] = []
                        user["submissions"].append(submission)
                        
                        # Update streak
                        update_streak(st.session_state.username)
                        
                        # Check badges
                        check_badges(st.session_state.username)
                        
                        # Update leaderboard
                        for entry in data["leaderboard"]:
                            if entry["username"] == st.session_state.username:
                                entry["totalPoints"] = user["totalPoints"]
                                entry["totalItemsSorted"] = user["totalItemsSorted"]
                                entry["badges"] = user["badges"]
                                break
                        
                        # Save
                        save_data(data)
                        
                        st.success(f"🎉 Earned {result['points']} points!")
                        st.balloons()

def page_leaderboard():
    """Leaderboard page"""
    st.markdown("<h1 style='text-align: center; color: #1B4332;'>🏆 Community Leaderboard</h1>", unsafe_allow_html=True)
    
    data = load_data()
    
    # City filter
    selected_city = st.selectbox(
        "Filter by city",
        ["Global"] + list(set([u["city"] for u in data["users"].values()]))
    )
    
    # Filter leaderboard
    if selected_city == "Global":
        leaderboard = sorted(data["leaderboard"], key=lambda x: x["totalPoints"], reverse=True)
    else:
        leaderboard = sorted(
            [entry for entry in data["leaderboard"] if entry["city"] == selected_city],
            key=lambda x: x["totalPoints"],
            reverse=True
        )
    
    # Display
    if not leaderboard:
        st.info("No users yet")
    else:
        for rank, entry in enumerate(leaderboard[:20], 1):
            # Rank emoji and styling
            if rank == 1:
                rank_emoji = "🥇"
            elif rank == 2:
                rank_emoji = "🥈"
            elif rank == 3:
                rank_emoji = "🥉"
            else:
                rank_emoji = f"#{rank}"
            
            # Get user stats
            user = data["users"].get(entry["username"], {})
            submissions = user.get("submissions", [])
            
            # Calculate stats
            avg_confidence = 0
            if submissions:
                confidences = [s.get("confidence", 0) for s in submissions]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Bin breakdown
            bin_counts = {}
            for sub in submissions:
                bin_type = sub.get("bin", "unknown")
                bin_counts[bin_type] = bin_counts.get(bin_type, 0) + 1
            
            # Build badges HTML
            badges_html = ""
            if entry.get('badges'):
                for badge in entry['badges']:
                    badges_html += f"<span style='display: inline-block; background: #e8f5f0; color: #1B4332; padding: 4px 10px; border-radius: 12px; margin-right: 5px; font-size: 0.8em;'>{badge['name']}</span>"
            
            badges_section = f"<div style='margin-top: 8px;'>{badges_html}</div>" if badges_html else ""
            
            # Bin type display
            bin_display = ""
            for bin_type, count in sorted(bin_counts.items()):
                emoji = {"recycling": "♻️", "compost": "🌱", "landfill": "🗑️", "special": "⚠️"}.get(bin_type, "📦")
                bin_display += f"<span style='margin-right: 15px;'>{emoji} {count}</span>"
            
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #d4e8e0; border-left: 3px solid #2D6A4F;
                        padding: 15px; border-radius: 6px; margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="display: flex; align-items: center; gap: 15px; flex: 1;">
                        <h2 style="margin: 0; font-size: 1.5em;">{rank_emoji}</h2>
                        <div>
                            <h3 style="margin: 0; color: #1B4332; font-size: 1.1em;">👤 {entry['username']}</h3>
                            <p style="margin: 5px 0 0 0; color: #2D6A4F; font-size: 0.9em;">📍 {entry['city']}</p>
                            <p style="margin: 5px 0 0 0; color: #555555; font-size: 0.85em;">{bin_display}</p>
                        </div>
                    </div>
                    <div style="text-align: right; white-space: nowrap;">
                        <h3 style="margin: 0; color: #2D6A4F; font-size: 1.3em; font-weight: 600;">⭐ {entry['totalPoints']}</h3>
                        <p style="margin: 5px 0 0 0; color: #555555; font-size: 0.9em;">♻️ {entry['totalItemsSorted']} items</p>
                        <p style="margin: 5px 0 0 0; color: #555555; font-size: 0.85em;">🎯 {avg_confidence:.0%} confidence</p>
                        <p style="margin: 5px 0 0 0; color: #555555; font-size: 0.85em;">🌍 CO₂: -{user.get('stats', {}).get('co2Saved', 0):.1f}kg</p>
                    </div>
                </div>
                {badges_section}
            </div>
            """, unsafe_allow_html=True)

def page_profile():
    """User profile page"""
    st.markdown(f"# 👤 Profile - {st.session_state.username}")
    
    data = load_data()
    user = data["users"][st.session_state.username]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Statistics")
        st.write(f"**City:** {user['city']}")
        st.write(f"**Joined:** {user['joinedAt'][:10]}")
        st.write(f"**Total Points:** {user['totalPoints']}")
        st.write(f"**Items Sorted:** {user['totalItemsSorted']}")
        st.write(f"**Longest Streak:** {user['longestStreak']} days")
    
    with col2:
        st.subheader("🌍 Environmental Impact")
        st.write(f"**CO₂ Avoided:** {user['stats']['co2Saved']:.2f} kg")
        st.write(f"**Water Saved:** {user['stats']['waterSaved']:.1f} liters")
        st.write(f"**Trees Saved:** {user['stats']['treesSaved']:.3f}")
    
    if user["badges"]:
        st.subheader("🏆 Badges")
        badge_cols = st.columns(len(user["badges"]))
        for i, badge in enumerate(user["badges"]):
            with badge_cols[i]:
                st.info(badge["name"])
    
    # Logout
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.username = None
        st.session_state.user_city = None
        st.rerun()

def page_insights():
    """Public insights page - City trends and statistics"""
    st.markdown("# 📈 City Insights & Trends")
    st.markdown("*AI-powered waste analysis for your community*")
    
    data = load_data()
    cities = sorted(set([u["city"] for u in data["users"].values()]))
    
    selected_city = st.selectbox("Select City", cities)
    
    if selected_city:
        stats = get_city_statistics(selected_city)
        
        if stats is None:
            st.info("No data yet for this city")
        else:
            # Top metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total Items", stats["total_submissions"])
            with col2:
                st.metric("♻️ Recycling %", f"{(stats['recycling_count']/stats['total_submissions']*100):.0f}%")
            with col3:
                st.metric("🌱 Compost %", f"{(stats['compost_count']/stats['total_submissions']*100):.0f}%")
            with col4:
                st.metric("✅ Verified Rate", f"{stats['verified_rate']:.0f}%")
            
            # Waste breakdown pie chart
            st.subheader("♻️ Waste Distribution")
            waste_data = {
                "Recycling": stats["recycling_count"],
                "Compost": stats["compost_count"],
                "Landfill": stats["landfill_count"],
                "Special": stats["special_count"]
            }
            waste_df = pd.DataFrame(list(waste_data.items()), columns=["Bin Type", "Count"])
            fig = px.pie(waste_df, values="Count", names="Bin Type", 
                        color_discrete_map={"Recycling": "#2ecc71", "Compost": "#27ae60", 
                                          "Landfill": "#e74c3c", "Special": "#f39c12"})
            st.plotly_chart(fig, use_container_width=True)
            
            # Most common items
            if stats["common_items"]:
                st.subheader("🔝 Most Common Items")
                items_df = pd.DataFrame(list(stats["common_items"].items()), columns=["Item", "Count"])
                fig = px.bar(items_df, x="Item", y="Count", title="Waste Items Frequency")
                st.plotly_chart(fig, use_container_width=True)
            
            # Avg confidence
            st.subheader("🎯 AI Classification Confidence")
            st.metric("Average Confidence Score", f"{stats['avg_confidence']:.1%}")
            st.info("Higher confidence = more accurate classifications")

def page_admin_analytics():
    """Admin analytics page - FiftyOne and submission analysis"""
    st.markdown("# 📊 Admin Analytics Dashboard")
    
    # Admin password check
    admin_password = st.text_input("Admin Password", type="password")
    if admin_password != "admin123":
        st.error("Unauthorized")
        return
    
    st.success("✅ Admin Access Granted")
    
    # Get analytics data
    df = get_analytics_data()
    
    if df.empty:
        st.info("No submissions yet")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Submissions", len(df))
    with col2:
        st.metric("Unique Users", df['username'].nunique())
    with col3:
        st.metric("Cities", df['city'].nunique())
    with col4:
        verified = len(df[df['verified'] == True]) if 'verified' in df.columns else 0
        st.metric("Verified Items", verified)
    
    # Submissions by city
    st.subheader("📍 Submissions by City")
    city_counts = df['city'].value_counts()
    fig = px.bar(city_counts, title="Submissions per City", labels={"value": "Count", "index": "City"})
    st.plotly_chart(fig, use_container_width=True)
    
    # Bin type distribution
    st.subheader("♻️ Classification Distribution")
    bin_counts = df['bin'].value_counts()
    fig = px.pie(values=bin_counts.values, names=bin_counts.index, title="Submissions by Bin Type")
    st.plotly_chart(fig, use_container_width=True)
    
    # Confidence histogram
    st.subheader("🎯 Confidence Scores Distribution")
    fig = px.histogram(df, x='confidence', nbins=20, title="AI Confidence Distribution")
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent submissions table
    st.subheader("📋 Recent Submissions")
    st.dataframe(df.sort_values('timestamp', ascending=False).head(10), use_container_width=True)

def page_quality_control():
    """Admin quality control - Review and verify submissions"""
    st.markdown("# ✅ Quality Control - Verify Classifications")
    
    # Admin password check
    admin_password = st.text_input("Admin Password", type="password", key="qc_password")
    if admin_password != "admin123":
        st.error("Unauthorized")
        return
    
    st.success("✅ QC Access Granted")
    
    data = load_data()
    df = get_analytics_data()
    
    if df.empty:
        st.info("No submissions to review")
        return
    
    # Filter unverified submissions
    unverified = df[df['verified'] == False]
    
    if len(unverified) == 0:
        st.success("✅ All submissions verified!")
        return
    
    st.info(f"**{len(unverified)} items pending review**")
    
    # Show unverified items
    col1, col2 = st.columns([3, 1])
    
    with col1:
        for idx, row in unverified.head(10).iterrows():
            with st.container():
                st.divider()
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    st.write(f"**User:** {row['username']} ({row['city']})")
                    st.write(f"**Item:** {row['item']}")
                    st.write(f"**Predicted Bin:** `{row['bin']}`")
                    st.write(f"**Confidence:** {row['confidence']:.1%}")
                    st.write(f"**Timestamp:** {row['timestamp']}")
                
                with col_b:
                    correct = st.button(f"✅ Correct", key=f"correct_{idx}")
                    incorrect = st.button(f"❌ Wrong", key=f"wrong_{idx}")
                    
                    if correct:
                        # Mark as verified in user data
                        for username in data["users"]:
                            for sub in data["users"][username].get("submissions", []):
                                if (sub["item"] == row['item'] and 
                                    sub["timestamp"] == row['timestamp']):
                                    sub["verified"] = True
                        save_data(data)
                        st.success("Marked as verified!")
                        st.rerun()
                    
                    if incorrect:
                        st.warning("Flagged for review")
    
    with col2:
        st.metric("Pending Review", len(unverified))
        st.metric("Verified", len(df[df['verified'] == True]))

def page_research_dashboard():
    """Research Dashboard - High-level insights for researchers"""
    st.markdown("# 📊 Research Dashboard")
    st.markdown("*Comprehensive waste classification data for research and analysis*")
    
    data = load_data()
    df = get_analytics_data()
    
    if df.empty:
        st.info("No data available yet. Classifications will appear here.")
        return
    
    # Overview metrics
    st.markdown("<h2 style='color: #1B4332;'>📈 Overall Statistics</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Submissions", len(df))
    with col2:
        st.metric("Unique Users", df['username'].nunique())
    with col3:
        st.metric("Cities Covered", df['city'].nunique())
    with col4:
        avg_confidence = df['confidence'].mean()
        st.metric("Avg AI Confidence", f"{avg_confidence:.1%}")
    
    # Verification stats
    col1, col2, col3 = st.columns(3)
    with col1:
        verified = len(df[df['verified'] == True])
        st.metric("Verified Items", verified)
    with col2:
        accuracy_rate = (verified / len(df) * 100) if len(df) > 0 else 0
        st.metric("Verification Rate", f"{accuracy_rate:.0f}%")
    with col3:
        st.metric("Date Range", f"{df['timestamp'].min().split('T')[0]} to {df['timestamp'].max().split('T')[0]}" if len(df) > 0 else "N/A")
    
    # Waste distribution
    st.markdown("---")
    st.markdown("<h2 style='color: #1B4332;'>♻️ Waste Classification Distribution</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        bin_counts = df['bin'].value_counts()
        fig = px.pie(values=bin_counts.values, names=bin_counts.index, 
                    title="Distribution by Waste Type",
                    color_discrete_map={"recycling": "#2ecc71", "compost": "#27ae60", 
                                      "landfill": "#e74c3c", "special": "#f39c12"})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Confidence distribution
        fig = px.histogram(df, x='confidence', nbins=20, 
                          title="AI Confidence Score Distribution",
                          labels={'confidence': 'Confidence Score', 'count': 'Submissions'})
        st.plotly_chart(fig, use_container_width=True)
    
    # City analysis
    st.markdown("---")
    st.markdown("<h2 style='color: #1B4332;'>📍 City-wise Analysis</h2>", unsafe_allow_html=True)
    
    city_data = df.groupby('city').agg({
        'username': 'nunique',
        'item': 'count',
        'confidence': 'mean'
    }).rename(columns={'username': 'Users', 'item': 'Submissions', 'confidence': 'Avg Confidence'})
    
    st.dataframe(city_data, use_container_width=True)
    
    # Item analysis
    st.markdown("---")
    st.markdown("<h2 style='color: #1B4332;'>📦 Top Waste Items Classified</h2>", unsafe_allow_html=True)
    
    item_counts = df['item'].value_counts().head(15)
    fig = px.bar(x=item_counts.values, y=item_counts.index, orientation='h',
                title="Top 15 Waste Items",
                labels={'x': 'Count', 'y': 'Item'},
                color=item_counts.values,
                color_continuous_scale="Greens")
    st.plotly_chart(fig, use_container_width=True)
    
    # User activity
    st.markdown("---")
    st.markdown("<h2 style='color: #1B4332;'>👥 Top Users by Activity</h2>", unsafe_allow_html=True)
    
    user_activity = df.groupby('username').agg({
        'item': 'count',
        'confidence': 'mean',
        'city': 'first'
    }).rename(columns={'item': 'Submissions', 'confidence': 'Avg Confidence', 'city': 'City'}).sort_values('Submissions', ascending=False).head(10)
    
    st.dataframe(user_activity, use_container_width=True)

def page_research_analytics():
    """Research Analytics - Detailed data export and analysis"""
    st.markdown("# 📋 Research Analytics & Data Export")
    st.markdown("*Download and analyze detailed classification data*")
    
    data = load_data()
    df = get_analytics_data()
    
    if df.empty:
        st.info("No data available yet.")
        return
    
    # Data export section
    st.markdown("<h2 style='color: #1B4332;'>💾 Data Export</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export submissions as CSV
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Submissions (CSV)",
            data=csv_data,
            file_name=f"wastewise_submissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Export user summary
        user_summary = []
        for username, user in data["users"].items():
            user_summary.append({
                "Username": username,
                "City": user["city"],
                "Total Points": user["totalPoints"],
                "Items Sorted": user["totalItemsSorted"],
                "Current Streak": user["currentStreak"],
                "Longest Streak": user["longestStreak"],
                "CO2 Saved (kg)": user["stats"]["co2Saved"],
                "Water Saved (L)": user["stats"]["waterSaved"],
                "Trees Saved": user["stats"]["treesSaved"],
                "Joined": user["joinedAt"][:10]
            })
        
        user_df = pd.DataFrame(user_summary)
        user_csv = user_df.to_csv(index=False)
        st.download_button(
            label="👥 Download User Summary (CSV)",
            data=user_csv,
            file_name=f"wastewise_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col3:
        # Export detailed JSON
        export_data = {
            "export_date": datetime.now().isoformat(),
            "summary": {
                "total_submissions": len(df),
                "unique_users": df['username'].nunique(),
                "cities": int(df['city'].nunique()),
                "avg_confidence": float(df['confidence'].mean()),
                "date_range": {
                    "start": df['timestamp'].min(),
                    "end": df['timestamp'].max()
                }
            },
            "data": data
        }
        
        import json as json_module
        json_data = json_module.dumps(export_data, indent=2)
        st.download_button(
            label="📊 Download Complete Data (JSON)",
            data=json_data,
            file_name=f"wastewise_full_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Data filtering and analysis
    st.markdown("---")
    st.markdown("<h2 style='color: #1B4332;'>🔍 Data Filtering & Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_city = st.selectbox("Filter by City", ["All"] + sorted(df['city'].unique().tolist()))
    
    with col2:
        selected_bin = st.selectbox("Filter by Waste Type", ["All"] + sorted(df['bin'].unique().tolist()))
    
    with col3:
        min_confidence = st.slider("Minimum Confidence", 0.0, 1.0, 0.0)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_city != "All":
        filtered_df = filtered_df[filtered_df['city'] == selected_city]
    if selected_bin != "All":
        filtered_df = filtered_df[filtered_df['bin'] == selected_bin]
    filtered_df = filtered_df[filtered_df['confidence'] >= min_confidence]
    
    st.info(f"Showing {len(filtered_df)} out of {len(df)} total submissions")
    
    # Show filtered data
    st.subheader("Filtered Submissions")
    st.dataframe(filtered_df.sort_values('timestamp', ascending=False), use_container_width=True)
    
    # Detailed statistics
    st.markdown("---")
    st.markdown("<h2 style='color: #1B4332;'>📊 Filtered Data Statistics</h2>", unsafe_allow_html=True)
    
    if len(filtered_df) > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Submissions", len(filtered_df))
        with col2:
            st.metric("Unique Users", filtered_df['username'].nunique())
        with col3:
            st.metric("Avg Confidence", f"{filtered_df['confidence'].mean():.1%}")
        with col4:
            verified = len(filtered_df[filtered_df['verified'] == True])
            st.metric("Verified", f"{verified}/{len(filtered_df)}")
        
        # Confidence distribution for filtered data
        fig = px.histogram(filtered_df, x='confidence', nbins=15,
                          title="Confidence Distribution (Filtered)")
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# MAIN APP
# ============================================

def main():
    """Main app"""
    init_user_session()
    
    if st.session_state.username is None:
        page_login()
    else:
        # Sidebar navigation
        st.sidebar.markdown(f"**👤 {st.session_state.username}**")
        st.sidebar.markdown(f"📍 {st.session_state.user_city}")
        st.sidebar.divider()
        
        # Check if admin
        is_admin = st.sidebar.checkbox("🔐 Admin Mode")
        
        if is_admin:
            page = st.sidebar.radio(
                "Admin Tools",
                ["Dashboard", "Sort", "Leaderboard", "Profile", "📊 Analytics", "✅ Quality Control", "📋 Research Dashboard", "📈 Research Analytics"]
            )
        else:
            page = st.sidebar.radio(
                "Navigate",
                ["Dashboard", "Sort", "Leaderboard", "📈 Insights", "Profile"]
            )
        
        if page == "Dashboard":
            page_dashboard()
        elif page == "Sort":
            page_sort()
        elif page == "Leaderboard":
            page_leaderboard()
        elif page == "📈 Insights":
            page_insights()
        elif page == "Profile":
            page_profile()
        elif page == "📊 Analytics":
            page_admin_analytics()
        elif page == "✅ Quality Control":
            page_quality_control()
        elif page == "📋 Research Dashboard":
            page_research_dashboard()
        elif page == "📈 Research Analytics":
            page_research_analytics()

if __name__ == "__main__":
    main()
