<div align="center">

# ✈️ VoyageAI – Smart Agentic Travel Planner

<p align="center">
  <b>An AI-powered, agentic travel itinerary planner built with Python, Streamlit, and Google Gemini LLMs.</b>
</p>

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen.svg?style=for-the-badge&logo=github)](https://pratham-shah-17.github.io/VoyageAI-/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini API](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Author: Pratham Shah](https://img.shields.io/badge/Author-Pratham%20Shah-brightgreen.svg)](https://github.com/pratham-shah-17)

---

### 🌐 Live Web Demo: [https://pratham-shah-17.github.io/VoyageAI-/](https://pratham-shah-17.github.io/VoyageAI-/)

---

</div>

## 🌟 Overview

**VoyageAI** is a smart agentic travel planner designed to curate comprehensive, realistic, and personalized day-by-day travel itineraries within seconds. 

By taking into account your **destination city**, **trip duration**, **budget tier**, and **travel vibe** (e.g., Foodie, Cultural, Adventure, Relaxed), VoyageAI uses Google Gemini AI to construct structured plans featuring:
- 🌅 **Morning Activities** (with locations, activity descriptions, and cost estimates)
- ☀️ **Afternoon Experiences** (curated local attractions and culinary spots)
- 🌙 **Evening Nightlife & Dining** (scenic vantage points and regional dinners)
- 💰 **Estimated Day & Total Trip Budgets**
- 💡 **Insider Travel Tips** tailored to local customs and transportation

---

## ✨ Features

- **🎯 Personalization Engine**: Select trip duration (1–14 days), budget level (*Budget*, *Mid-Range*, *Luxury*), and custom travel vibes.
- **🤖 Powered by Google Gemini**: Leverages `gemini-2.5-flash` or `gemini-1.5-flash` for intelligent, structured JSON itinerary generation.
- **⚡ Built-in Zero-Crash Fallback**: Includes an automatic fallback generator that seamlessly serves realistic mock itineraries if an API key is absent or rate-limited.
- **🎨 Glassmorphism Streamlit UI**: Dark mode dashboard featuring metric cards, time-of-day badges, and organized daily tab views.
- **📥 One-Click Export**:
  - Export complete itineraries as **Markdown (`.md`)** files.
  - Export beautiful formatted **PDF (`.pdf`)** files.

---

## 🛠️ Tech Stack

| Component | Technology Used |
| :--- | :--- |
| **Frontend & UI** | [Streamlit](https://streamlit.io/) |
| **LLM & AI Engine** | [Google Gemini API](https://ai.google.dev/) (`google-genai` / `google-generativeai`) |
| **Document Generation** | [FPDF2](https://pyfpdf.github.io/fpdf2/) |
| **Environment Management** | [python-dotenv](https://github.com/theskumar/python-dotenv) |
| **Language** | Python 3.10+ |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/pratham-shah-17/VoyageAI-.git
cd VoyageAI-
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup (Optional)
Create a `.env` file in the project root to store your Gemini API Key:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```
*(Alternatively, you can enter your API Key directly in the app sidebar).*

### 4. Launch the App
```bash
streamlit run app.py
```
Visit `http://localhost:8501` in your browser!

---

## 📂 Project Structure

```
VoyageAI/
├── app.py              # Main Streamlit Web Application (UI + Core Logic + Exports)
├── requirements.txt    # Application dependencies
├── .env.example        # Environment variable template
├── LICENSE             # MIT License (Pratham Shah)
└── README.md           # Project Documentation
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

Copyright (c) 2026 **Pratham Shah**

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/pratham-shah-17">Pratham Shah</a></sub>
</div>
