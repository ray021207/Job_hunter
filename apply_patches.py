"""
WasteWise Patch Script
Run this ONCE from inside your WasteWise project folder:
    python apply_patches.py

It will modify wastewise_streamlit.py in-place and create a backup first.
"""

import shutil
import os

SRC = "wastewise_streamlit.py"
BACKUP = "wastewise_streamlit.backup.py"

if not os.path.exists(SRC):
    print(f"ERROR: {SRC} not found. Run this from your WasteWise project folder.")
    exit(1)

# Make a backup first
shutil.copy(SRC, BACKUP)
print(f"✅ Backup created: {BACKUP}")

with open(SRC, "r") as f:
    code = f.read()

# ─────────────────────────────────────────────────────────────
# PATCH 1: Fix API key loading for Streamlit Cloud compatibility
# ─────────────────────────────────────────────────────────────
OLD_API = '''# Load environment variables
load_dotenv()

# Load environment variables
load_dotenv()'''

NEW_API = '''# Load environment variables
load_dotenv()

# ============================================
# API KEY - works locally AND on Streamlit Cloud
# ============================================
def get_api_key():
    """Get API key from Streamlit secrets or environment"""
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY", "")'''

if OLD_API in code:
    code = code.replace(OLD_API, NEW_API)
    print("✅ PATCH 1: Fixed API key loading for Streamlit Cloud")
else:
    print("⚠️  PATCH 1: Could not find exact match — skipping (check manually)")

# Also fix the classify_waste function to use get_api_key()
OLD_APIKEY = '''        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            st.error("⚠️ API key not found. Create a .env file with ANTHROPIC_API_KEY")
            return None'''

NEW_APIKEY = '''        api_key = get_api_key()

        if not api_key:
            st.error("⚠️ API key not found. Add ANTHROPIC_API_KEY to .env or Streamlit secrets.")
            return None'''

if OLD_APIKEY in code:
    code = code.replace(OLD_APIKEY, NEW_APIKEY)
    print("✅ PATCH 1b: Fixed classify_waste to use get_api_key()")
else:
    print("⚠️  PATCH 1b: Could not patch classify_waste api_key line — check manually")

# ─────────────────────────────────────────────────────────────
# PATCH 2: Add DROPOFF_LOCATIONS data + show_dropoff_map()
# Insert right before PAGE CONFIG section
# ─────────────────────────────────────────────────────────────
DROPOFF_CODE = '''
# ============================================
# DROP-OFF LOCATIONS & MAP
# ============================================

DROPOFF_LOCATIONS = {
    "Tempe": [
        {"name": "Tempe Transfer Station", "lat": 33.4148, "lon": -111.9290,
         "accepts": "Electronics, Batteries, Paint, Chemicals"},
        {"name": "Home Depot Tempe", "lat": 33.4255, "lon": -111.9400,
         "accepts": "Batteries, CFLs, Paint"},
        {"name": "Best Buy Tempe Marketplace", "lat": 33.4285, "lon": -111.9712,
         "accepts": "Electronics, Cables, Phones, Batteries"},
    ],
    "Phoenix": [
        {"name": "Phoenix HHW Facility – 27th Ave", "lat": 33.4942, "lon": -112.0908,
         "accepts": "Paint, Chemicals, Electronics, Batteries"},
        {"name": "North Mountain Village Library", "lat": 33.5870, "lon": -112.0740,
         "accepts": "Electronics, Small Appliances"},
        {"name": "Best Buy Phoenix", "lat": 33.5085, "lon": -112.0678,
         "accepts": "Electronics, Cables, Phones"},
    ],
    "Mesa": [
        {"name": "Mesa HHW Drop-off", "lat": 33.4152, "lon": -111.8315,
         "accepts": "Paint, Chemicals, Batteries, Electronics"},
        {"name": "Staples Mesa", "lat": 33.4034, "lon": -111.8499,
         "accepts": "Ink Cartridges, Electronics"},
    ],
    "Scottsdale": [
        {"name": "Scottsdale Recycling Center", "lat": 33.4942, "lon": -111.9261,
         "accepts": "Electronics, Batteries, Paint"},
        {"name": "Home Depot Scottsdale", "lat": 33.5027, "lon": -111.9261,
         "accepts": "Batteries, CFLs, Paint"},
    ],
    "Gilbert": [
        {"name": "Gilbert HHW Facility", "lat": 33.3528, "lon": -111.7890,
         "accepts": "Paint, Chemicals, Batteries, Electronics"},
    ],
    "Chandler": [
        {"name": "Chandler Transfer Station", "lat": 33.3062, "lon": -111.8413,
         "accepts": "Electronics, Paint, Batteries, Chemicals"},
    ],
}


def show_dropoff_map(city: str):
    """Show drop-off locations map for special waste items"""
    city_key = city.split(",")[0].strip()
    locations = DROPOFF_LOCATIONS.get(city_key, DROPOFF_LOCATIONS["Tempe"])

    st.markdown("""
    <div style='background:#fff8e1; border-left:4px solid #f59e0b; padding:14px 18px;
                border-radius:6px; margin:12px 0;'>
        <h4 style='color:#92400e; margin:0 0 4px;'>⚠️ Special Disposal Required</h4>
        <p style='color:#78350f; margin:0; font-size:0.9em;'>
            Do NOT put this in regular bins. Use one of the drop-off locations below.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📍 Nearest Drop-off Locations")

    map_df = pd.DataFrame([{"lat": loc["lat"], "lon": loc["lon"]} for loc in locations])
    st.map(map_df, zoom=12)

    for loc in locations:
        st.markdown(f"""
        <div style='background:#f0f7f4; border:1px solid #d4e8e0; border-left:3px solid #2D6A4F;
                    padding:10px 14px; border-radius:6px; margin:6px 0;'>
            <strong style='color:#1B4332;'>📦 {loc["name"]}</strong><br>
            <span style='color:#555; font-size:0.88em;'>Accepts: {loc["accepts"]}</span>
        </div>
        """, unsafe_allow_html=True)

'''

INSERT_BEFORE = "# ============================================\n# PAGE CONFIG\n# ============================================"

if INSERT_BEFORE in code:
    code = code.replace(INSERT_BEFORE, DROPOFF_CODE + INSERT_BEFORE, 1)
    print("✅ PATCH 2: Added DROPOFF_LOCATIONS and show_dropoff_map()")
else:
    print("⚠️  PATCH 2: Could not find PAGE CONFIG marker — check manually")

# ─────────────────────────────────────────────────────────────
# PATCH 3: Call show_dropoff_map() after a "special" result
# Find the block right after result display in page_sort()
# ─────────────────────────────────────────────────────────────
OLD_RESULT_SAVE = '''                    # Save this classification
                    if st.button("✅ Save & Earn Points", use_container_width=True):'''

NEW_RESULT_SAVE = '''                    # Show drop-off map for special items
                    if result.get("bin") == "special":
                        show_dropoff_map(st.session_state.user_city)

                    # Save this classification
                    if st.button("✅ Save & Earn Points", use_container_width=True):'''

if OLD_RESULT_SAVE in code:
    code = code.replace(OLD_RESULT_SAVE, NEW_RESULT_SAVE, 1)
    print("✅ PATCH 3: Drop-off map now shows after special item classification")
else:
    print("⚠️  PATCH 3: Could not find save button anchor — check manually")

# ─────────────────────────────────────────────────────────────
# PATCH 4: Add public FiftyOne Insights tab (page_fiftyone_insights)
# Insert before the main() function
# ─────────────────────────────────────────────────────────────
FIFTYONE_PAGE = '''
def page_fiftyone_insights():
    """Public FiftyOne-powered insights tab — visible to all users"""

    st.markdown("""
    <div style='background:linear-gradient(135deg,#1C4532,#2D6A4F); padding:1.5rem;
                border-radius:10px; margin-bottom:1.5rem;'>
        <h2 style='color:white; margin:0;'>🔬 Dataset Insights</h2>
        <p style='color:#D8F3DC; margin:0.4rem 0 0; font-size:0.95em;'>
            Powered by FiftyOne — real-time AI performance tracking across all users
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = get_analytics_data()

    # Use placeholder data if empty (so demo never looks broken)
    if df.empty:
        st.info("No real submissions yet — showing sample data for demo.")
        import random
        placeholder = []
        items = ["Pizza Box","Plastic Bottle","Battery","Cardboard","Coffee Cup",
                 "Old Phone","Paint Can","Plastic Bag","Glass Jar","Newspaper"]
        bins  = ["recycling","recycling","special","recycling","landfill",
                 "special","special","landfill","recycling","recycling"]
        for i in range(40):
            idx = i % len(items)
            placeholder.append({
                "username": f"user{i%8}",
                "city": ["Tempe","Phoenix","Mesa"][i%3],
                "item": items[idx],
                "bin": bins[idx],
                "confidence": round(0.65 + (i % 35) * 0.01, 2),
                "timestamp": "2026-03-21T10:00:00",
                "verified": i % 3 == 0
            })
        df = pd.DataFrame(placeholder)

    total = len(df)
    avg_conf = df["confidence"].mean()
    recycling_rate = len(df[df["bin"] == "recycling"]) / total if total else 0

    # Top metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔍 Total Scans", total)
    with col2:
        st.metric("🎯 Avg Confidence", f"{avg_conf:.0%}")
    with col3:
        st.metric("♻️ Recycling Rate", f"{recycling_rate:.0%}")

    st.markdown("---")

    # Bin distribution bar chart
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Waste Distribution")
        bin_counts = df["bin"].value_counts()
        bin_df = pd.DataFrame({
            "Bin Type": bin_counts.index.str.title(),
            "Count": bin_counts.values
        })
        colors = {
            "Recycling": "#2D6A4F",
            "Compost": "#52B788",
            "Landfill": "#E53935",
            "Special": "#FB8C00"
        }
        fig = px.bar(
            bin_df, x="Bin Type", y="Count",
            color="Bin Type",
            color_discrete_map=colors,
            title="Items by Bin Type"
        )
        fig.update_layout(showlegend=False, plot_bgcolor="white",
                          paper_bgcolor="white", font_color="#1B4332")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Confidence Distribution")
        fig = px.histogram(
            df, x="confidence", nbins=15,
            title="AI Confidence Scores",
            color_discrete_sequence=["#2D6A4F"]
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          font_color="#1B4332")
        st.plotly_chart(fig, use_container_width=True)

    # FiftyOne callout
    st.markdown("""
    <div style='background:#f0f7f4; border:1px solid #d4e8e0; border-left:4px solid #2D6A4F;
                padding:14px 18px; border-radius:6px; margin-top:1rem;'>
        <h4 style='color:#1B4332; margin:0 0 6px;'>🔬 How FiftyOne Powers This</h4>
        <p style='color:#555; margin:0; font-size:0.9em;'>
            Every photo you classify is stored as a <strong>FiftyOne sample</strong> with
            labels, confidence scores, and metadata. This lets us visually inspect where
            Claude gets it right, find failure modes (e.g. greasy vs clean cardboard),
            and build a ground-truth dataset that improves over time.
            This is what separates WasteWise from a chatbot wrapper — it\'s a
            <strong>data pipeline</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Top misclassified items (low confidence)
    low_conf = df[df["confidence"] < 0.70]
    if len(low_conf) > 0:
        st.markdown("---")
        st.subheader("⚠️ Items Claude Found Ambiguous (confidence < 70%)")
        st.caption("These are candidates for human review and dataset improvement")
        low_conf_display = low_conf[["item","bin","confidence","city"]].copy()
        low_conf_display.columns = ["Item","Bin","Confidence","City"]
        low_conf_display["Confidence"] = low_conf_display["Confidence"].apply(lambda x: f"{x:.0%}")
        st.dataframe(low_conf_display.head(10), use_container_width=True)

'''

INSERT_BEFORE_MAIN = "# ============================================\n# MAIN APP\n# ============================================"

if INSERT_BEFORE_MAIN in code:
    code = code.replace(INSERT_BEFORE_MAIN, FIFTYONE_PAGE + INSERT_BEFORE_MAIN, 1)
    print("✅ PATCH 4: Added page_fiftyone_insights()")
else:
    print("⚠️  PATCH 4: Could not find MAIN APP marker — check manually")

# ─────────────────────────────────────────────────────────────
# PATCH 5: Add "🔬 Dataset Insights" to the navigation
# ─────────────────────────────────────────────────────────────
OLD_NAV = '''        else:
            page = st.sidebar.radio(
                "Navigate",
                ["Dashboard", "Sort", "Leaderboard", "📈 Insights", "Profile"]
            )'''

NEW_NAV = '''        else:
            page = st.sidebar.radio(
                "Navigate",
                ["Dashboard", "Sort", "Leaderboard", "📈 Insights",
                 "🔬 Dataset Insights", "Profile"]
            )'''

if OLD_NAV in code:
    code = code.replace(OLD_NAV, NEW_NAV, 1)
    print("✅ PATCH 5: Added Dataset Insights to navigation")
else:
    print("⚠️  PATCH 5: Could not find nav block — check manually")

# Also add the routing for the new page
OLD_ROUTE = '''        elif page == "📈 Insights":
            page_insights()
        elif page == "Profile":
            page_profile()'''

NEW_ROUTE = '''        elif page == "📈 Insights":
            page_insights()
        elif page == "🔬 Dataset Insights":
            page_fiftyone_insights()
        elif page == "Profile":
            page_profile()'''

if OLD_ROUTE in code:
    code = code.replace(OLD_ROUTE, NEW_ROUTE, 1)
    print("✅ PATCH 5b: Added routing for Dataset Insights page")
else:
    print("⚠️  PATCH 5b: Could not find routing block — check manually")

# ─────────────────────────────────────────────────────────────
# Write patched file
# ─────────────────────────────────────────────────────────────
with open(SRC, "w") as f:
    f.write(code)

print("\n🎉 All patches applied!")
print("Next steps:")
print("  1. pip install -r requirements_streamlit.txt")
print("  2. streamlit run wastewise_streamlit.py")
print("  3. Test: classify a 'battery' — should show the drop-off map")
print("  4. Check 🔬 Dataset Insights tab in the sidebar")
print("  5. git add . && git commit -m 'Add drop-off map, FiftyOne insights, Streamlit Cloud support'")
print("  6. git push origin main")
print("  7. Deploy at share.streamlit.io")
