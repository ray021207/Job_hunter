# ♻️ WasteWise - AI Waste Sorting App with FiftyOne Analytics

**Upload a waste photo → Get instant AI recommendations → Earn points & badges → See city insights**

Smart waste disposal with leaderboards, environmental impact tracking, and FiftyOne-powered analytics. Works on phones! 📱

## ✨ Features

- 🤖 **AI Classification** - Claude Sonnet 4.6 analyzes your waste in seconds
- 📊 **Leaderboard** - Compete with friends, see who's sorted most
- 🏆 **Badges** - Unlock achievements as you sort more items
- 🌍 **Impact Tracking** - Watch your CO₂ avoided, water saved, trees saved
- � **City Insights** - See waste trends & statistics for your community
- 🔬 **FiftyOne Analytics** - (Admin) Full dataset visualization & analysis
- ✅ **Quality Control** - (Admin) Review & verify classifications
- �📱 **Mobile Friendly** - Works perfectly on phones
- 🚀 **Deploy Anywhere** - Free hosting on Streamlit Cloud

## 🏆 Badges You Can Unlock

- 🎖️ First Step → Sort 1 item
- 🎖️ Quick Starter → Sort 10 items
- 🎖️ Eco Warrior → Sort 50 items
- 🎖️ Legendary Sorter → Sort 100 items
- 🔥 7-Day Streak → Sort 7 consecutive days
- 🔥 30-Day Legend → Sort 30 consecutive days

## 📊 Admin Features (Password Protected)

### 📈 Analytics Dashboard
- View all submissions across all users
- See waste distribution by city
- Track AI confidence scores
- Identify most common waste items
- Monitor verification rates
- **Access:** Check "🔐 Admin Mode" box, password: `admin123`

### ✅ Quality Control
- Review unverified submissions
- Mark classifications as correct/incorrect
- Track verification progress
- Improve AI accuracy from real user data
- **Access:** Same admin password

### 📊 City Insights (Public for All Users)
- See city-wide waste trends
- Top waste items by community
- Recycling vs compost percentage
- Average AI confidence
- Educational insights

## 🚀 Quick Start (2 minutes)

### 1️⃣ Install
```bash
pip install -r requirements_streamlit.txt
```

### 2️⃣ Configure
```bash
cp .env.example .env
```
Open `.env` and add your Anthropic API key from https://console.anthropic.com

### 3️⃣ Run
```bash
streamlit run wastewise_streamlit.py
```

**Opens at:** `http://localhost:8501`

## 📱 Access on Your Phone

You can access the app on your phone in **3 ways**:

### Option 1: Same WiFi Network (Easiest for Demo!)
```bash
streamlit run wastewise_streamlit.py --server.address 0.0.0.0
```
Then on your phone, open: `http://YOUR-COMPUTER-IP:8501`

To find your computer IP:
- Windows: Run `ipconfig` in terminal, look for "IPv4 Address"
- Mac/Linux: Run `ifconfig`, look for inet address

### Option 2: Local Network with ngrok (Quick Share)
```bash
pip install ngrok
streamlit run wastewise_streamlit.py &
ngrok http 8501
```
Share the ngrok URL with friends - works anywhere!

### Option 3: Deploy to Streamlit Cloud (Permanent)
```bash
git add .
git commit -m "WasteWise demo"
git push origin main
```

Then:
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select repo + main file: `wastewise_streamlit.py`
5. Deploy → Add API key to Secrets
6. Your app is live! Share the link with anyone

**Everyone can access on their phones via the link!**

## 🎮 How to Use

1. **Create Account** → Pick username, choose city
2. **Upload Photo** → Take photo with phone or upload from gallery
3. **See Classification** → AI shows: item name, bin type, confidence
4. **Earn Points** → Save to leaderboard, gain points
5. **Check Leaderboard** → See rankings, compete with friends
6. **Unlock Badges** → Get achievements for streaks & milestones
7. **Track Impact** → Watch your environmental stats grow

## 🏆 Badges You Can Unlock

- 🎖️ First Step → Sort 1 item
- 🎖️ Quick Starter → Sort 10 items
- 🎖️ Eco Warrior → Sort 50 items
- 🎖️ Legendary Sorter → Sort 100 items
- 🔥 7-Day Streak → Sort 7 consecutive days
- 🔥 30-Day Legend → Sort 30 consecutive days

## 📊 Points System

Each item earns points based on bin type × confidence:
- ♻️ Recycling: 100 pts
- 🌱 Compost: 120 pts
- ⚠️ Special (hazmat): 150 pts
- 🗑️ Landfill: 25 pts

## 🔧 Customization

### Change Cities
Edit line ~300 in `wastewise_streamlit.py`:
```python
city = st.selectbox("City", ["Tempe", "Phoenix", "Denver", "NYC"])
```

### Adjust Points
Edit `calculate_points()` function:
```python
base_points = {
    "recycling": 100,      # Change these numbers
    "compost": 120,
}
```

### Add More Badges
Edit `check_badges()` function with new badge conditions.

## � FiftyOne Integration

The app automatically collects all user submissions into a FiftyOne dataset for analytics:

### What Gets Tracked
- User submissions (photos, timestamps, usernames)
- AI classifications (item name, bin type, confidence)
- City location
- Verification status (admin quality control)

### Admin Analytics Features
1. **Dashboard** - See submissions by city, bin type distribution, confidence scores
2. **Verification** - Mark correct/incorrect classifications to improve AI
3. **Insights** - Generate city trends, common waste items, recycling rates

### How to Access
1. Login to app
2. Check "🔐 Admin Mode" in sidebar
3. Password: `admin123`

### Data Usage
- Understand waste patterns in your community
- Improve AI accuracy from real corrections
- Create reports on waste trends
- Generate insights for education

## �🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not found" | Open `.env`, add your key from console.anthropic.com |
| "ModuleNotFoundError" | Run `pip install -r requirements_streamlit.txt` |
| "Can't access on phone" | Make sure phone is on same WiFi, use computer IP |
| "Port 8501 in use" | Run `streamlit run wastewise_streamlit.py --server.port 8502` |

## 📁 What's What

```
wastewise_streamlit.py         ← The entire app (single file)
requirements_streamlit.txt     ← Packages to install
wastewise_data.json            ← Your user data (auto-created)
.env                           ← Your API key (you create this)
.env.example                   ← Template (copy to .env)
```

## 💡 Tips for Demo

**Show it on your phone:**
```bash
streamlit run wastewise_streamlit.py --server.address 0.0.0.0
```
- Open on your phone: `http://[YOUR-IP]:8501`
- Create a test account
- Upload a waste photo
- Show the leaderboard
- Explain the badges & impact tracking

**Best demo items:** plastic bottle, pizza box, hazardous item, compost

## 🎯 Next Steps

1. **Local Demo** → Run above, open on phone via WiFi
2. **Quick Share** → Deploy free via Streamlit Cloud (git push)
3. **Customize** → Edit cities, points, badges
4. **Invite Friends** → Share the Streamlit Cloud link

## 📞 API Cost

- Per image: ~$0.003 (very cheap!)
- 1 user, 20 images/month: ~$0.06
- Get free tier at https://console.anthropic.com

---

**Ready? Run:** `streamlit run wastewise_streamlit.py` ♻️
