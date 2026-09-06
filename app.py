"""
VoyageAI – Smart Agentic Travel Planner
Author: Pratham Shah
GitHub: https://github.com/pratham-shah-17/VoyageAI-.git
License: MIT
"""

import os
import json
import re
import io
from typing import Dict, Any, List
import streamlit as st

# Try importing Google Gemini SDKs gracefully
GEMINI_GENAI_AVAILABLE = False
GEMINI_LEGACY_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    GEMINI_GENAI_AVAILABLE = True
except ImportError:
    pass

if not GEMINI_GENAI_AVAILABLE:
    try:
        import google.generativeai as legacy_genai
        GEMINI_LEGACY_AVAILABLE = True
    except ImportError:
        pass

# Try importing FPDF for PDF export
FPDF_AVAILABLE = False
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    pass


# ==============================================================================
# PAGE CONFIGURATION & CUSTOM STYLING
# ==============================================================================
st.set_page_config(
    page_title="VoyageAI – Smart Agentic Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern visual design
st.markdown("""
<style>
    /* Main Theme Overrides */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
    }
    
    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(168, 85, 247, 0.15));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #cbd5e1;
        max-width: 700px;
        margin: 0 auto;
    }

    /* Cards & Containers */
    .trip-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(8px);
    }
    
    .activity-card {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #818cf8;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .activity-card.afternoon {
        border-left-color: #f59e0b;
    }
    .activity-card.evening {
        border-left-color: #ec4899;
    }
    
    .cost-badge {
        background: rgba(129, 140, 248, 0.2);
        color: #a5b4fc;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        float: right;
    }
    
    /* Metrics Header */
    .metric-box {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Target Buttons */
    .stButton>button {
        border-radius: 12px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        font-weight: 600;
        border: none;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# FALLBACK MOCK DATA GENERATOR
# ==============================================================================
def generate_mock_itinerary(destination: str, days: int, budget: str, vibe: str) -> Dict[str, Any]:
    """Generates structured fallback mock data when API key is missing or fails."""
    dest_clean = destination.strip().title() if destination else "Paris, France"
    
    mock_activities = {
        "Foodie": [
            ("Local Artisan Bakery & Espresso", "Sample fresh croissants, pastries, and specialty coffee at a historic local café.", "$15 - $25"),
            ("Gourmet Food Market Tour", "Explore vibrant market stalls, tasting regional cheeses, cured meats, and fresh produce.", "$45 - $70"),
            ("Fine Dining & Wine Pairing", "Indulge in a multi-course dinner paired with somatic selected local wines.", "$90 - $160")
        ],
        "Cultural": [
            ("Historic Museum & Gallery Walk", "Visit iconic art galleries, historical landmarks, and world-renowned collections.", "$20 - $40"),
            ("Guided Architecture & Old Town Tour", "Walk through historic quarters with a local expert storyteller.", "$30 - $55"),
            ("Traditional Music & Performing Arts", "Experience an evening theatrical performance or classic musical concert.", "$50 - $110")
        ],
        "Adventure": [
            ("Sunrise Scenic Trail Hike", "Ascend nearby panoramic vantage points for spectacular mountain or city views.", "$10 - $30"),
            ("Outdoor Kayaking & River Excursion", "Paddle along scenic waterways with experienced adventure guides.", "$50 - $85"),
            ("Rooftop Sunset Lounge & Night Skyline", "Unwind after an active day with dynamic views and signature cocktails.", "$40 - $75")
        ],
        "Relaxed": [
            ("Botanical Gardens & Morning Promenade", "Stroll through tranquil gardens and picturesque waterfront pathways.", "Free - $15"),
            ("Thermal Spa & Wellness Session", "Enjoy soothing hydrotherapy pools, massages, and relaxation lounges.", "$70 - $130"),
            ("Sunset Beach / Park Picnic", "Watch the horizon melt into night with artisanal snacks and local beverages.", "$25 - $45")
        ]
    }
    
    selected_vibe_key = "Cultural"
    for v_key in mock_activities:
        if v_key.lower() in vibe.lower():
            selected_vibe_key = v_key
            break
            
    vibe_acts = mock_activities[selected_vibe_key]
    
    daily_itineraries = []
    total_est = 0
    
    for d in range(1, days + 1):
        m_act, m_desc, m_cost = vibe_acts[0]
        a_act, a_desc, a_cost = vibe_acts[1]
        e_act, e_desc, e_cost = vibe_acts[2]
        
        daily_itineraries.append({
            "day": d,
            "theme": f"Day {d}: Exploring {dest_clean}'s Top Highlights ({vibe})",
            "morning": {
                "activity": f"{m_act} in {dest_clean}",
                "location": f"Central District, {dest_clean}",
                "description": m_desc,
                "est_cost": m_cost
            },
            "afternoon": {
                "activity": f"{a_act} Experience",
                "location": f"Historic Center, {dest_clean}",
                "description": a_desc,
                "est_cost": a_cost
            },
            "evening": {
                "activity": f"{e_act}",
                "location": f"Downtown Waterfront, {dest_clean}",
                "description": e_desc,
                "est_cost": e_cost
            },
            "daily_tip": "Purchase a local day transit pass to save money on rides.",
            "total_day_cost": f"${60 * d + 50} - ${100 * d + 90}"
        })
        
    return {
        "destination": dest_clean,
        "trip_summary": f"A curated {days}-day {budget.lower()} trip to {dest_clean} tailored for a {vibe.lower()} traveler.",
        "estimated_total_cost": f"${days * 120} - ${days * 250} USD (excluding flights)",
        "daily_itineraries": daily_itineraries,
        "insider_tips": [
            f"Tipping in {dest_clean}: Check local service charge policies before tipping.",
            "Download offline maps on your phone for seamless navigation.",
            "Book top museum and activity tickets at least 3 days in advance."
        ],
        "is_mock": True
    }


# ==============================================================================
# LLM PROMPT & API CALL LOGIC
# ==============================================================================
def generate_itinerary_llm(
    destination: str, 
    days: int, 
    budget: str, 
    vibe: str, 
    notes: str, 
    api_key: str
) -> Dict[str, Any]:
    """Queries Gemini API for structured travel planner output with automatic fallback."""
    if not api_key:
        return generate_mock_itinerary(destination, days, budget, vibe)
        
    prompt = f"""
You are an expert AI Travel Planner creating a personalized day-by-day itinerary.

TRIP DETAILS:
- Destination: {destination}
- Duration: {days} days
- Budget Tier: {budget}
- Travel Vibe: {vibe}
- Additional Notes/Preferences: {notes if notes else 'None'}

REQUIREMENTS:
1. Provide a detailed, realistic day-by-day travel plan for EXACTLY {days} days.
2. For EVERY single day, provide specific Morning, Afternoon, and Evening activities.
3. Include realistic location names, descriptions, and estimated cost ranges in USD.
4. Output STRICT, VALID JSON ONLY (no markdown formatting around json if possible, or json block).

JSON SCHEMA TO FOLLOW:
{{
  "destination": "{destination}",
  "trip_summary": "Short 2-3 sentence overview of the trip experience",
  "estimated_total_cost": "$XXX - $YYY USD",
  "daily_itineraries": [
    {{
      "day": 1,
      "theme": "Theme of the day",
      "morning": {{
        "activity": "Activity Name",
        "location": "Specific location or spot",
        "description": "Description of activity and why to visit",
        "est_cost": "$XX - $YY"
      }},
      "afternoon": {{
        "activity": "Activity Name",
        "location": "Specific location or spot",
        "description": "Description of activity",
        "est_cost": "$XX - $YY"
      }},
      "evening": {{
        "activity": "Activity Name",
        "location": "Specific location or spot",
        "description": "Description of activity",
        "est_cost": "$XX - $YY"
      }},
      "daily_tip": "Insider tip for this day",
      "total_day_cost": "$XX - $YY"
    }}
  ],
  "insider_tips": [
    "Tip 1 regarding transport/culture/saving money",
    "Tip 2 regarding local food or customs",
    "Tip 3 regarding best times to visit"
  ]
}}
"""

    raw_text = ""
    try:
        if GEMINI_GENAI_AVAILABLE:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            raw_text = response.text
        elif GEMINI_LEGACY_AVAILABLE:
            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            raw_text = response.text
        else:
            # Fallback if libraries are missing
            return generate_mock_itinerary(destination, days, budget, vibe)

        # Parse JSON output from LLM
        clean_json = raw_text.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
            
        parsed_data = json.loads(clean_json.strip())
        parsed_data["is_mock"] = False
        return parsed_data
        
    except Exception as e:
        st.warning(f"⚠️ API call or parsing encountered an issue ({str(e)}). Switching to fallback itinerary.")
        return generate_mock_itinerary(destination, days, budget, vibe)


# ==============================================================================
# EXPORT HELPERS (MARKDOWN & PDF)
# ==============================================================================
def create_markdown_export(data: Dict[str, Any]) -> str:
    """Creates clean Markdown representation of the itinerary."""
    md = f"# ✈️ VoyageAI Travel Plan: {data.get('destination', 'Trip')}\n\n"
    md += f"**Trip Summary:** {data.get('trip_summary', '')}\n\n"
    md += f"**Estimated Total Cost:** {data.get('estimated_total_cost', 'N/A')}\n\n"
    md += "---\n\n"
    
    for day_data in data.get("daily_itineraries", []):
        md += f"## Day {day_data.get('day')}: {day_data.get('theme', '')}\n"
        md += f"*Estimated Day Budget: {day_data.get('total_day_cost', 'N/A')}*\n\n"
        
        m = day_data.get("morning", {})
        md += f"### 🌅 Morning: {m.get('activity', 'Morning Activity')}\n"
        md += f"- **Location:** {m.get('location', 'N/A')}\n"
        md += f"- **Description:** {m.get('description', '')}\n"
        md += f"- **Est. Cost:** {m.get('est_cost', 'N/A')}\n\n"
        
        a = day_data.get("afternoon", {})
        md += f"### ☀️ Afternoon: {a.get('activity', 'Afternoon Activity')}\n"
        md += f"- **Location:** {a.get('location', 'N/A')}\n"
        md += f"- **Description:** {a.get('description', '')}\n"
        md += f"- **Est. Cost:** {a.get('est_cost', 'N/A')}\n\n"
        
        e = day_data.get("evening", {})
        md += f"### 🌙 Evening: {e.get('activity', 'Evening Activity')}\n"
        md += f"- **Location:** {e.get('location', 'N/A')}\n"
        md += f"- **Description:** {e.get('description', '')}\n"
        md += f"- **Est. Cost:** {e.get('est_cost', 'N/A')}\n\n"
        
        if day_data.get("daily_tip"):
            md += f"> 💡 **Daily Tip:** {day_data.get('daily_tip')}\n\n"
        md += "---\n\n"
        
    tips = data.get("insider_tips", [])
    if tips:
        md += "## 💡 Insider Travel Tips\n"
        for t in tips:
            md += f"- {t}\n"
            
    return md


def sanitize_text(text: str) -> str:
    """Strips non-latin1 characters for safe PDF generation with standard Helvetica font."""
    if not text:
        return ""
    # Remove emoji & non-latin1 characters
    return text.encode("latin-1", "ignore").decode("latin-1")


def create_pdf_export(data: Dict[str, Any]) -> bytes:
    """Generates a clean PDF binary using FPDF."""
    if not FPDF_AVAILABLE:
        return b""
        
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Helvetica", "B", 18)
    dest = sanitize_text(data.get("destination", "Travel Plan"))
    pdf.cell(w=pdf.epw, h=10, text=f"VoyageAI Travel Plan: {dest}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)
    
    # Summary
    pdf.set_font("Helvetica", "I", 10)
    summary = sanitize_text(data.get("trip_summary", ""))
    pdf.multi_cell(w=pdf.epw, h=6, text=summary, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Cost
    pdf.set_font("Helvetica", "B", 11)
    cost = sanitize_text(data.get("estimated_total_cost", ""))
    pdf.cell(w=pdf.epw, h=8, text=f"Estimated Total Cost: {cost}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Days
    for day_data in data.get("daily_itineraries", []):
        day_num = day_data.get("day", 1)
        theme = sanitize_text(day_data.get("theme", ""))
        day_cost = sanitize_text(day_data.get("total_day_cost", ""))
        
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(w=pdf.epw, h=8, text=f"Day {day_num}: {theme} ({day_cost})", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        
        for period, title in [("morning", "Morning"), ("afternoon", "Afternoon"), ("evening", "Evening")]:
            act = day_data.get(period, {})
            act_name = sanitize_text(act.get("activity", ""))
            loc = sanitize_text(act.get("location", ""))
            desc = sanitize_text(act.get("description", ""))
            est = sanitize_text(act.get("est_cost", ""))
            
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(w=pdf.epw, h=6, text=f"  [{title}] {act_name} - Est. Cost: {est}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(w=pdf.epw, h=5, text=f"   Location: {loc}", new_x="LMARGIN", new_y="NEXT")
            pdf.multi_cell(w=pdf.epw, h=5, text=f"   {desc}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
        tip = sanitize_text(day_data.get("daily_tip", ""))
        if tip:
            pdf.set_font("Helvetica", "I", 9)
            pdf.multi_cell(w=pdf.epw, h=5, text=f"   Daily Tip: {tip}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        
    tips = data.get("insider_tips", [])
    if tips:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(w=pdf.epw, h=8, text="Insider Tips & Guidance", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        for t in tips:
            pdf.multi_cell(w=pdf.epw, h=5, text=f"- {sanitize_text(t)}", new_x="LMARGIN", new_y="NEXT")
            
    return bytes(pdf.output())


# ==============================================================================
# MAIN STREAMLIT APPLICATION INTERFACE
# ==============================================================================
def main():
    # Hero Header Banner
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">✈️ VoyageAI</div>
        <div class="hero-subtitle">Smart Agentic Travel Planner — Powered by Generative AI</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --------------------------------------------------------------------------
    # SIDEBAR: API KEY & CONFIGURATION
    # --------------------------------------------------------------------------
    st.sidebar.title("⚙️ AI Engine Settings")
    
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.sidebar.text_input(
        "Google Gemini API Key",
        value=env_api_key,
        type="password",
        help="Enter your Gemini API key. If left blank or invalid, the app uses realistic fallback mock data."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Quick Tips")
    st.sidebar.info(
        "• Leave API Key blank to preview with fast mock data.\n"
        "• Export your complete plan to PDF or Markdown once generated.\n"
        "• Works with Gemini 2.5 Flash & 1.5 Flash."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("👨‍💻 Created by **Pratham Shah** | MIT License")
    
    # --------------------------------------------------------------------------
    # MAIN FORM INPUTS
    # --------------------------------------------------------------------------
    st.markdown("### 🌍 Plan Your Next Journey")
    
    col1, col2 = st.columns(2)
    
    with col1:
        destination = st.text_input(
            "📍 Destination City / Region",
            value="Kyoto, Japan",
            placeholder="e.g. Tokyo, Paris, Rome, Bali"
        )
        
        days = st.slider(
            "🗓️ Trip Duration (Days)",
            min_value=1,
            max_value=14,
            value=3,
            step=1
        )

    with col2:
        budget = st.selectbox(
            "💰 Budget Tier",
            options=["Budget 💰", "Mid-Range 💳", "Luxury ✨"],
            index=1
        )
        
        vibe = st.selectbox(
            "✨ Travel Vibe",
            options=[
                "Foodie & Culinary 🍕",
                "Cultural & Historic 🏛️",
                "Adventure & Nature 🏔️",
                "Relaxed & Wellness 🧘‍♀️",
                "Nightlife & Party 🎉",
                "Shopping & Fashion 🛍️"
            ],
            index=1
        )
        
    notes = st.text_area(
        "📝 Special Requests / Preferences (Optional)",
        placeholder="e.g. Traveling with family, vegetarian food options, love photo spots, walking-friendly pace...",
        height=80
    )
    
    st.markdown("")
    generate_btn = st.button("🚀 Generate Smart Itinerary", use_container_width=True)
    
    # --------------------------------------------------------------------------
    # ITINERARY GENERATION & DISPLAY
    # --------------------------------------------------------------------------
    if generate_btn:
        if not destination.strip():
            st.error("Please enter a destination city or country!")
            return
            
        with st.spinner(f"🤖 VoyageAI is orchestrating your {days}-day itinerary for {destination}..."):
            itinerary_data = generate_itinerary_llm(
                destination=destination,
                days=days,
                budget=budget,
                vibe=vibe,
                notes=notes,
                api_key=user_api_key
            )
            st.session_state["current_itinerary"] = itinerary_data

    # Display Itinerary if present in session state
    if "current_itinerary" in st.session_state:
        data = st.session_state["current_itinerary"]
        
        st.markdown("---")
        
        if data.get("is_mock", False):
            st.info("ℹ️ Showing fallback demo itinerary. Add a valid Gemini API Key in the sidebar to enable live AI generation.")
            
        # Overview Cards
        dest_display = data.get("destination", destination)
        st.markdown(f"## 🗺️ Itinerary for {dest_display}")
        st.write(data.get("trip_summary", ""))
        
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{days} Days</div>
                <div class="metric-label">Duration</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{budget.split()[0]}</div>
                <div class="metric-label">Budget Tier</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{data.get('estimated_total_cost', 'N/A')}</div>
                <div class="metric-label">Estimated Total Cost</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Day Tabs Display
        daily_list = data.get("daily_itineraries", [])
        if daily_list:
            tab_titles = [f"Day {d.get('day', i+1)}" for i, d in enumerate(daily_list)]
            tabs = st.tabs(tab_titles)
            
            for idx, tab in enumerate(tabs):
                day_info = daily_list[idx]
                with tab:
                    st.markdown(f"### {day_info.get('theme', f'Day {idx+1}')}")
                    st.caption(f"Estimated Day Budget: {day_info.get('total_day_cost', 'N/A')}")
                    
                    # Morning
                    m = day_info.get("morning", {})
                    st.markdown(f"""
                    <div class="activity-card">
                        <span class="cost-badge">{m.get('est_cost', 'Free')}</span>
                        <h4>🌅 Morning: {m.get('activity', '')}</h4>
                        <p><b>📍 Location:</b> {m.get('location', '')}</p>
                        <p>{m.get('description', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Afternoon
                    a = day_info.get("afternoon", {})
                    st.markdown(f"""
                    <div class="activity-card afternoon">
                        <span class="cost-badge">{a.get('est_cost', 'Free')}</span>
                        <h4>☀️ Afternoon: {a.get('activity', '')}</h4>
                        <p><b>📍 Location:</b> {a.get('location', '')}</p>
                        <p>{a.get('description', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Evening
                    e = day_info.get("evening", {})
                    st.markdown(f"""
                    <div class="activity-card evening">
                        <span class="cost-badge">{e.get('est_cost', 'Free')}</span>
                        <h4>🌙 Evening: {e.get('activity', '')}</h4>
                        <p><b>📍 Location:</b> {e.get('location', '')}</p>
                        <p>{e.get('description', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if day_info.get("daily_tip"):
                        st.info(f"💡 **Daily Tip:** {day_info.get('daily_tip')}")
                        
        # Insider Tips Section
        tips = data.get("insider_tips", [])
        if tips:
            st.markdown("---")
            st.markdown("### 💡 Insider Travel Tips & Local Advice")
            for tip in tips:
                st.markdown(f"- {tip}")
                
        # ----------------------------------------------------------------------
        # EXPORT & DOWNLOAD OPTIONS
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 📥 Export & Download Itinerary")
        
        exp_col1, exp_col2 = st.columns(2)
        
        # Markdown Export
        md_content = create_markdown_export(data)
        with exp_col1:
            st.download_button(
                label="📄 Download Markdown (.md)",
                data=md_content,
                file_name=f"{dest_display.lower().replace(' ', '_')}_itinerary.md",
                mime="text/markdown",
                use_container_width=True
            )
            
        # PDF Export
        with exp_col2:
            if FPDF_AVAILABLE:
                pdf_bytes = create_pdf_export(data)
                st.download_button(
                    label="📕 Download PDF (.pdf)",
                    data=pdf_bytes,
                    file_name=f"{dest_display.lower().replace(' ', '_')}_itinerary.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.button("📕 PDF Export (Install fpdf2)", disabled=True, use_container_width=True)


if __name__ == "__main__":
    main()
