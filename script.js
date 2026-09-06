/* ==========================================================================
   VoyageAI – Smart Agentic Travel Planner
   Interactive Application Script (Client-Side JS & Gemini API Integrator)
   Author: Pratham Shah
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const destInput = document.getElementById('destInput');
    const daysSlider = document.getElementById('daysSlider');
    const daysBadge = document.getElementById('daysBadge');
    const notesInput = document.getElementById('notesInput');
    const generateBtn = document.getElementById('generateBtn');
    
    const settingsToggleBtn = document.getElementById('settingsToggleBtn');
    const apiSettingsPanel = document.getElementById('apiSettingsPanel');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
    
    const placeholderState = document.getElementById('placeholderState');
    const loadingState = document.getElementById('loadingState');
    const itineraryDisplay = document.getElementById('itineraryDisplay');
    
    const exportMdBtn = document.getElementById('exportMdBtn');
    const exportPdfBtn = document.getElementById('exportPdfBtn');

    // Local State
    let selectedBudget = 'Mid-Range';
    let selectedVibe = 'Cultural & Historic';
    let currentItineraryData = null;

    // Load Saved API Key
    const savedApiKey = localStorage.getItem('voyageai_gemini_key') || '';
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }

    // Toggle Settings Panel
    settingsToggleBtn.addEventListener('click', () => {
        apiSettingsPanel.classList.toggle('active');
    });

    saveApiKeyBtn.addEventListener('click', () => {
        const key = apiKeyInput.value.trim();
        localStorage.setItem('voyageai_gemini_key', key);
        alert(key ? '✅ Gemini API Key saved locally!' : 'ℹ️ API Key cleared. App will use smart mock itineraries.');
        apiSettingsPanel.classList.remove('active');
    });

    // Destination Chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            destInput.value = chip.dataset.dest;
        });
    });

    // Slider Live Value
    daysSlider.addEventListener('input', (e) => {
        daysBadge.textContent = `${e.target.value} Days`;
    });

    // Budget Options Toggle
    document.querySelectorAll('.budget-option').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.budget-option').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedBudget = btn.dataset.value;
        });
    });

    // Vibe Options Toggle
    document.querySelectorAll('.vibe-option').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.vibe-option').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedVibe = btn.dataset.value;
        });
    });

    // Generate Button Click
    generateBtn.addEventListener('click', async () => {
        const dest = destInput.value.trim();
        const days = parseInt(daysSlider.value);
        const notes = notesInput.value.trim();
        const apiKey = apiKeyInput.value.trim();

        if (!dest) {
            alert('Please enter a destination city or country!');
            return;
        }

        // Show Loading State
        placeholderState.style.display = 'none';
        itineraryDisplay.style.display = 'none';
        loadingState.style.display = 'block';

        // Simulate step messages
        const loadingSubtext = document.getElementById('loadingSubtext');
        const steps = [
            `Connecting to AI engine...`,
            `Analyzing best highlights for ${dest}...`,
            `Structuring ${days}-day ${selectedVibe.toLowerCase()} itinerary...`,
            `Calculating realistic budget estimates...`
        ];

        let stepIdx = 0;
        const stepInterval = setInterval(() => {
            if (stepIdx < steps.length) {
                loadingSubtext.textContent = steps[stepIdx];
                stepIdx++;
            }
        }, 600);

        try {
            let data = null;
            if (apiKey) {
                data = await fetchGeminiItinerary(dest, days, selectedBudget, selectedVibe, notes, apiKey);
            }

            if (!data) {
                // Fallback to Smart Mock Generator
                data = generateSmartMockItinerary(dest, days, selectedBudget, selectedVibe);
            }

            clearInterval(stepInterval);
            currentItineraryData = data;
            renderItinerary(data);

        } catch (err) {
            console.error(err);
            clearInterval(stepInterval);
            const fallbackData = generateSmartMockItinerary(dest, days, selectedBudget, selectedVibe);
            currentItineraryData = fallbackData;
            renderItinerary(fallbackData);
        } finally {
            loadingState.style.display = 'none';
            itineraryDisplay.style.display = 'block';
        }
    });

    // --------------------------------------------------------------------------
    // GEMINI LIVE API CALL (Client-Side)
    // --------------------------------------------------------------------------
    async function fetchGeminiItinerary(dest, days, budget, vibe, notes, apiKey) {
        const prompt = `
You are an expert AI Travel Planner. Create a realistic ${days}-day trip to ${dest}.
Budget Tier: ${budget}
Travel Vibe: ${vibe}
Special Requests: ${notes || 'None'}

Return ONLY valid JSON matching this exact structure:
{
  "destination": "${dest}",
  "trip_summary": "Short 2-3 sentence trip overview",
  "estimated_total_cost": "$XXX - $YYY USD",
  "daily_itineraries": [
    {
      "day": 1,
      "theme": "Theme of Day 1",
      "morning": { "activity": "Activity Name", "location": "Location Spot", "description": "Short description", "est_cost": "$15 - $25" },
      "afternoon": { "activity": "Activity Name", "location": "Location Spot", "description": "Short description", "est_cost": "$30 - $50" },
      "evening": { "activity": "Activity Name", "location": "Location Spot", "description": "Short description", "est_cost": "$40 - $70" },
      "daily_tip": "Insider tip for Day 1",
      "total_day_cost": "$85 - $145"
    }
  ],
  "insider_tips": [ "Local tip 1", "Local tip 2", "Local tip 3" ]
}
`;

        const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }]
            })
        });

        if (!response.ok) return null;

        const resData = await response.json();
        const text = resData?.candidates?.[0]?.content?.parts?.[0]?.text || '';
        
        let cleanJson = text.trim();
        if (cleanJson.startsWith('```json')) cleanJson = cleanJson.substring(7);
        if (cleanJson.startsWith('```')) cleanJson = cleanJson.substring(3);
        if (cleanJson.endsWith('```')) cleanJson = cleanJson.substring(0, cleanJson.length - 3);

        const parsed = JSON.parse(cleanJson.strip ? cleanJson.strip() : cleanJson);
        parsed.isMock = false;
        return parsed;
    }

    // --------------------------------------------------------------------------
    // SMART FALLBACK MOCK GENERATOR
    // --------------------------------------------------------------------------
    function generateSmartMockItinerary(dest, days, budget, vibe) {
        const destTitle = dest.split(',')[0].trim().replace(/\b\w/g, l => l.toUpperCase());

        const mockRepo = {
            'Foodie': [
                ['Artisan Bakery & Specialty Espresso', 'Sample fresh croissants, pastries, and single-origin coffee at a historic café.', '$15 - $25'],
                ['Gourmet Food Market & Tasting Tour', 'Explore vibrant market stalls, tasting regional cheeses, charcuterie, and street food.', '$45 - $70'],
                ['Chef’s Table & Wine Pairing Dinner', 'Indulge in a multi-course dinner paired with somatic selected local wines.', '$90 - $160']
            ],
            'Cultural': [
                ['Historic Museum & Art Gallery Walk', 'Visit iconic landmarks, historical monuments, and world-renowned art collections.', '$20 - $40'],
                ['Guided Old Town & Architecture Tour', 'Stroll through historic quarters with an expert local storyteller.', '$30 - $55'],
                ['Traditional Musical & Performing Arts', 'Experience an evening of traditional music or classic live theater.', '$50 - $110']
            ],
            'Adventure': [
                ['Sunrise Trail Hike & Panoramic Viewpoint', 'Ascend nearby vantage points for breathtaking morning city skyline views.', '$10 - $25'],
                ['River Kayaking & Outdoor Excursion', 'Paddle along scenic natural waterways with experienced adventure guides.', '$50 - $85'],
                ['Rooftop Sunset Lounge & Night Skyline', 'Unwind after an active day with signature cocktails and panoramic views.', '$40 - $75']
            ],
            'Relaxed': [
                ['Botanical Gardens & Promenade Walk', 'Stroll through tranquil gardens and picturesque waterfront pathways.', 'Free - $15'],
                ['Thermal Spa & Hydrotherapy Session', 'Enjoy soothing hot springs, massages, and relaxation lounges.', '$70 - $130'],
                ['Sunset Picnic at City Park', 'Watch the horizon melt into twilight with local wine and artisanal snacks.', '$20 - $40']
            ]
        };

        let key = 'Cultural';
        for (let k in mockRepo) {
            if (vibe.toLowerCase().includes(k.toLowerCase())) {
                key = k;
                break;
            }
        }

        const acts = mockRepo[key];
        const dailyItineraries = [];

        for (let d = 1; d <= days; d++) {
            const m = acts[0];
            const a = acts[1];
            const e = acts[2];

            dailyItineraries.push({
                day: d,
                theme: `Day ${d}: ${destTitle}'s Highlights & Local Secrets`,
                morning: { activity: `${m[0]} in ${destTitle}`, location: `Central District, ${destTitle}`, description: m[1], est_cost: m[2] },
                afternoon: { activity: `${a[0]}`, location: `Historic Center, ${destTitle}`, description: a[1], est_cost: a[2] },
                evening: { activity: `${e[0]}`, location: `Downtown Waterfront, ${destTitle}`, description: e[1], est_cost: e[2] },
                daily_tip: `Purchase a local day transit pass to save on transportation.`,
                total_day_cost: `$${50 + d * 30} - $${100 + d * 50}`
            });
        }

        return {
            destination: destTitle,
            trip_summary: `A curated ${days}-day ${budget.toLowerCase()} trip to ${destTitle} tailored for a ${vibe.toLowerCase()} traveler.`,
            estimated_total_cost: `$${days * 110} - $${days * 230} USD`,
            daily_itineraries: dailyItineraries,
            insider_tips: [
                `Tipping in ${destTitle}: Check local service charge policies before tipping.`,
                `Download offline transit maps for easy navigation.`,
                `Book top museum and venue tickets at least 3 days in advance.`
            ],
            isMock: true
        };
    }

    // --------------------------------------------------------------------------
    // RENDER ITINERARY UI
    // --------------------------------------------------------------------------
    function renderItinerary(data) {
        document.getElementById('displayDest').textContent = data.destination;
        document.getElementById('displaySummary').textContent = data.trip_summary;
        document.getElementById('metricDays').textContent = `${data.daily_itineraries.length} Days`;
        document.getElementById('metricBudget').textContent = selectedBudget.split(' ')[0];
        document.getElementById('metricVibe').textContent = selectedVibe.split(' ')[0];
        document.getElementById('metricCost').textContent = data.estimated_total_cost;

        // Render Tabs
        const tabsNav = document.getElementById('tabsNav');
        tabsNav.innerHTML = '';

        data.daily_itineraries.forEach((dayData, idx) => {
            const btn = document.createElement('button');
            btn.className = `tab-btn ${idx === 0 ? 'active' : ''}`;
            btn.textContent = `Day ${dayData.day}`;
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                renderDayDetails(dayData);
            });
            tabsNav.appendChild(btn);
        });

        // Render Initial Day
        if (data.daily_itineraries.length > 0) {
            renderDayDetails(data.daily_itineraries[0]);
        }

        // Render Insider Tips
        const tipsList = document.getElementById('tipsList');
        tipsList.innerHTML = '';
        (data.insider_tips || []).forEach(tip => {
            const li = document.createElement('li');
            li.style.marginBottom = '6px';
            li.textContent = tip;
            tipsList.appendChild(li);
        });
    }

    function renderDayDetails(dayData) {
        const dayContainer = document.getElementById('dayDetailsContainer');
        dayContainer.innerHTML = `
            <div style="margin-bottom: 20px;">
                <h3 style="font-size: 1.3rem; font-weight: 700; color: var(--text-primary);">${dayData.theme}</h3>
                <span style="font-size: 0.85rem; color: var(--accent-indigo);">Est. Day Budget: ${dayData.total_day_cost}</span>
            </div>
            
            <div class="activities-list">
                <!-- Morning -->
                <div class="activity-card">
                    <div class="period-header">
                        <div class="period-title">🌅 Morning: ${dayData.morning.activity}</div>
                        <span class="cost-tag">${dayData.morning.est_cost}</span>
                    </div>
                    <div class="location-tag">📍 ${dayData.morning.location}</div>
                    <div class="activity-desc">${dayData.morning.description}</div>
                </div>

                <!-- Afternoon -->
                <div class="activity-card afternoon">
                    <div class="period-header">
                        <div class="period-title">☀️ Afternoon: ${dayData.afternoon.activity}</div>
                        <span class="cost-tag">${dayData.afternoon.est_cost}</span>
                    </div>
                    <div class="location-tag">📍 ${dayData.afternoon.location}</div>
                    <div class="activity-desc">${dayData.afternoon.description}</div>
                </div>

                <!-- Evening -->
                <div class="activity-card evening">
                    <div class="period-header">
                        <div class="period-title">🌙 Evening: ${dayData.evening.activity}</div>
                        <span class="cost-tag">${dayData.evening.est_cost}</span>
                    </div>
                    <div class="location-tag">📍 ${dayData.evening.location}</div>
                    <div class="activity-desc">${dayData.evening.description}</div>
                </div>

                <!-- Daily Tip -->
                ${dayData.daily_tip ? `
                <div class="daily-tip-box">
                    💡 <b>Daily Tip:</b> ${dayData.daily_tip}
                </div>` : ''}
            </div>
        `;
    }

    // --------------------------------------------------------------------------
    // EXPORT HANDLERS (Markdown & PDF)
    // --------------------------------------------------------------------------
    exportMdBtn.addEventListener('click', () => {
        if (!currentItineraryData) return;
        const d = currentItineraryData;
        let md = `# ✈️ VoyageAI Travel Plan: ${d.destination}\n\n`;
        md += `**Summary:** ${d.trip_summary}\n\n`;
        md += `**Estimated Total Cost:** ${d.estimated_total_cost}\n\n---\n\n`;

        d.daily_itineraries.forEach(day => {
            md += `## Day ${day.day}: ${day.theme}\n`;
            md += `*Estimated Day Cost: ${day.total_day_cost}*\n\n`;
            md += `### 🌅 Morning: ${day.morning.activity}\n- Location: ${day.morning.location}\n- Est Cost: ${day.morning.est_cost}\n- ${day.morning.description}\n\n`;
            md += `### ☀️ Afternoon: ${day.afternoon.activity}\n- Location: ${day.afternoon.location}\n- Est Cost: ${day.afternoon.est_cost}\n- ${day.afternoon.description}\n\n`;
            md += `### 🌙 Evening: ${day.evening.activity}\n- Location: ${day.evening.location}\n- Est Cost: ${day.evening.est_cost}\n- ${day.evening.description}\n\n`;
            if (day.daily_tip) md += `> 💡 **Tip:** ${day.daily_tip}\n\n`;
            md += `---\n\n`;
        });

        const blob = new Blob([md], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${d.destination.toLowerCase().replace(/ /g, '_')}_itinerary.md`;
        a.click();
    });

    exportPdfBtn.addEventListener('click', () => {
        window.print();
    });
});
