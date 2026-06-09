import asyncio
import base64
import os
from playwright.async_api import async_playwright

def get_base64_image(path):
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded_string}"

# ── Image paths (relative to project root) ─────────────────────────
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
img1_path = os.path.join(PROJECT_ROOT, "assets", "Interface.png")
img2_path = os.path.join(PROJECT_ROOT, "assets", "Evidence-Backed.png")
img3_path = os.path.join(PROJECT_ROOT, "assets", "Log.png")

img1_b64 = get_base64_image(img1_path) if os.path.exists(img1_path) else ""
img2_b64 = get_base64_image(img2_path) if os.path.exists(img2_path) else ""
img3_b64 = get_base64_image(img3_path) if os.path.exists(img3_path) else ""

html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TruthSeeker</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #05050f;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.1);
            --accent-1: #38bdf8;
            --accent-2: #c084fc;
            --accent-3: #fb7185;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
        }}

        /* Slide dimensions: 1080x1350 for LinkedIn 4:5 portrait format */
        .slide {{
            width: 1080px;
            height: 1350px;
            position: relative;
            overflow: hidden;
            padding: 100px;
            display: flex;
            flex-direction: column;
            page-break-after: always;
            background: radial-gradient(circle at 100% 0%, rgba(56, 189, 248, 0.15) 0%, transparent 40%),
                        radial-gradient(circle at 0% 100%, rgba(192, 132, 252, 0.15) 0%, transparent 40%),
                        var(--bg-color);
        }}

        /* Glassmorphism background elements */
        .glow-blob {{
            position: absolute;
            border-radius: 50%;
            filter: blur(100px);
            z-index: 0;
            opacity: 0.5;
        }}
        
        .content-z {{
            position: relative;
            z-index: 10;
        }}

        h1 {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 96px;
            line-height: 1.1;
            margin-bottom: 40px;
            background: linear-gradient(to right, var(--accent-1), var(--accent-2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -2px;
        }}

        h2 {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 64px;
            margin-bottom: 60px;
            color: var(--text-main);
        }}

        h3 {{
            font-size: 40px;
            margin-bottom: 20px;
            color: var(--accent-1);
        }}

        p {{
            font-size: 32px;
            line-height: 1.6;
            color: var(--text-muted);
            margin-bottom: 30px;
        }}

        .glass-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 32px;
            padding: 50px;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            margin-bottom: 40px;
        }}

        .flex-row {{
            display: flex;
            gap: 40px;
        }}

        .flex-col {{
            display: flex;
            flex-direction: column;
            flex: 1;
        }}

        ul {{
            list-style-type: none;
        }}

        li {{
            font-size: 28px;
            color: var(--text-muted);
            margin-bottom: 24px;
            display: flex;
            align-items: flex-start;
        }}

        li::before {{
            content: "✦";
            color: var(--accent-2);
            margin-right: 20px;
            font-size: 24px;
        }}

        .tag-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: auto;
        }}

        .tag {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 12px 24px;
            border-radius: 100px;
            font-size: 20px;
            font-weight: 600;
            color: var(--text-main);
        }}

        .footer {{
            position: absolute;
            bottom: 60px;
            left: 100px;
            right: 100px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--card-border);
            padding-top: 30px;
        }}

        .footer p {{
            font-size: 20px;
            margin: 0;
        }}

        .verdict-box {{
            border-left: 8px solid;
            padding-left: 30px;
            margin-top: 30px;
            margin-bottom: 50px;
        }}

        .verdict-true {{ border-color: var(--success); }}
        .verdict-false {{ border-color: var(--danger); }}
        .verdict-unverifiable {{ border-color: var(--warning); }}

        .verdict-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 36px;
            margin-bottom: 15px;
            color: var(--text-main);
        }}

        .verdict-label {{
            font-weight: 800;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 20px;
            letter-spacing: 2px;
            text-transform: uppercase;
            display: inline-block;
            margin-bottom: 20px;
        }}

        .label-true {{ background: rgba(16, 185, 129, 0.2); color: var(--success); }}
        .label-false {{ background: rgba(239, 68, 68, 0.2); color: var(--danger); }}

        /* Flow diagram specific */
        .flow-node {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            padding: 30px;
            text-align: center;
            position: relative;
            z-index: 2;
        }}

        .flow-arrow {{
            text-align: center;
            font-size: 40px;
            color: var(--accent-1);
            margin: 20px 0;
            opacity: 0.7;
        }}

        .highlight {{ color: var(--text-main); font-weight: 600; }}
        
        .code-block {{
            font-family: monospace;
            background: rgba(0,0,0,0.5);
            padding: 30px;
            border-radius: 16px;
            font-size: 22px;
            color: var(--accent-1);
            border: 1px solid var(--card-border);
        }}

        .app-screenshot {{
            width: 100%;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
            border: 1px solid var(--card-border);
            margin-bottom: 30px;
            object-fit: cover;
        }}
    </style>
</head>
<body>

    <!-- SLIDE 1: Cover -->
    <div class="slide">
        <div class="glow-blob" style="width: 600px; height: 600px; background: var(--accent-1); top: -200px; left: -200px;"></div>
        <div class="glow-blob" style="width: 500px; height: 500px; background: var(--accent-2); bottom: -100px; right: -100px;"></div>
        
        <div class="content-z" style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
            <p style="color: var(--accent-1); font-weight: 600; letter-spacing: 4px; font-size: 24px; text-transform: uppercase; margin-bottom: 20px;">Project Showcase</p>
            <h1 style="font-size: 110px;">TruthSeeker</h1>
            <p style="font-size: 42px; color: var(--text-main); max-width: 800px; line-height: 1.4;">
                An AI Fact-Checking Pipeline powered by Corrective RAG (CRAG).
            </p>
            <br>
            <p style="font-size: 32px; max-width: 800px;">
                Intelligently retrieves evidence, grades it, searches the live web as a fallback, and generates accurate, evidence-backed verdicts.
            </p>

            <div class="tag-container" style="margin-top: 60px;">
                <div class="tag">Python</div>
                <div class="tag">LangGraph</div>
                <div class="tag">Llama 3.3 70B</div>
                <div class="tag">Supabase</div>
                <div class="tag">Streamlit</div>
            </div>
        </div>

        <div class="footer">
            <p style="color: var(--text-main); font-weight: 600;">Hassan Ali</p>
            <p>AI Engineer</p>
        </div>
    </div>

    <!-- SLIDE 2: The Problem -->
    <div class="slide">
        <div class="content-z">
            <h2>The Problem with RAG</h2>
            
            <div class="glass-card">
                <h3>Standard RAG Blind Spots</h3>
                <p>Standard Retrieval-Augmented Generation blindly trusts whatever it pulls from the database.</p>
                <ul>
                    <li>If it retrieves irrelevant documents, it hallucinates.</li>
                    <li>If the database lacks the answer, it gives up or guesses.</li>
                    <li>No quality control on the evidence itself.</li>
                </ul>
            </div>

            <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.05);">
                <h3 style="color: var(--text-main);">The CRAG Solution</h3>
                <p><span class="highlight">Corrective RAG</span> adds a self-reflection loop.</p>
                <ul>
                    <li><span class="highlight">Grades</span> documents for relevance before using them.</li>
                    <li><span class="highlight">Filters</span> out noise automatically.</li>
                    <li><span class="highlight">Falls back</span> to live web search if the database falls short.</li>
                </ul>
            </div>
        </div>
        <div class="footer">
            <p>TruthSeeker Architecture</p>
            <p>Swipe ➔</p>
        </div>
    </div>

    <!-- SLIDE 3: The Pipeline -->
    <div class="slide">
        <div class="glow-blob" style="width: 800px; height: 800px; background: rgba(56, 189, 248, 0.1); top: 20%; left: 10%;"></div>
        
        <div class="content-z">
            <h2>The 4-Node Pipeline</h2>
            <p>Built with LangGraph state machine routing.</p>
            
            <div style="margin-top: 40px;">
                <div class="flow-node" style="border-color: var(--accent-1);">
                    <h3 style="margin: 0; font-size: 32px;">1. Retrieve</h3>
                    <p style="margin: 10px 0 0 0; font-size: 24px;">Cosine similarity search via Supabase pgvector</p>
                </div>
                
                <div class="flow-arrow">↓</div>
                
                <div class="flow-node" style="border-color: var(--accent-2);">
                    <h3 style="margin: 0; font-size: 32px; color: var(--accent-2);">2. Grade Documents</h3>
                    <p style="margin: 10px 0 0 0; font-size: 24px;">Llama 3.3 filters out irrelevant docs from results</p>
                </div>
                
                <div style="display: flex; gap: 40px; margin: 20px 0;">
                    <div style="flex: 1; text-align: center; border: 1px dashed var(--accent-3); border-radius: 24px; padding: 20px;">
                        <p style="font-size: 20px; margin: 0; color: var(--accent-3);">If < 2 Relevant Docs</p>
                        <div class="flow-arrow" style="margin: 10px 0; color: var(--accent-3);">↓</div>
                        <h3 style="margin: 0; font-size: 28px; color: var(--accent-3);">3. Web Search</h3>
                        <p style="margin: 10px 0 0 0; font-size: 20px;">Tavily API fallback</p>
                    </div>
                    <div style="flex: 1; display: flex; flex-direction: column; justify-content: center; text-align: center;">
                        <p style="font-size: 20px; margin: 0;">If Sufficient Evidence</p>
                        <div class="flow-arrow" style="margin: 10px 0;">↓</div>
                    </div>
                </div>
                
                <div class="flow-node" style="border-color: var(--success);">
                    <h3 style="margin: 0; font-size: 32px; color: var(--success);">4. Generate Verdict</h3>
                    <p style="margin: 10px 0 0 0; font-size: 24px;">Produce TRUE / FALSE / UNVERIFIABLE with reasoning</p>
                </div>
            </div>
        </div>
        <div class="footer">
            <p>TruthSeeker Architecture</p>
            <p>Swipe ➔</p>
        </div>
    </div>

    <!-- SLIDE 4: The Interface & Output -->
    <div class="slide">
        <div class="glow-blob" style="width: 700px; height: 700px; background: rgba(16, 185, 129, 0.15); top: 10%; right: 0%;"></div>
        
        <div class="content-z">
            <h2>The Interface</h2>
            <p>A clean, dynamic Streamlit UI that delivers instant, structured verdicts.</p>
            
            <img src="{img1_b64}" class="app-screenshot" alt="TruthSeeker Input" />
            
            <div style="margin-top: 20px;">
                <p style="color: var(--text-main); font-size: 28px;">The system automatically flags myths like <i>"Humans only use 10% of their brain"</i> as <b>FALSE</b> and states its stance.</p>
            </div>
        </div>
        <div class="footer">
            <p>TruthSeeker In Action</p>
            <p>Swipe ➔</p>
        </div>
    </div>

    <!-- SLIDE 5: Reasoning & Evidence -->
    <div class="slide">
        <div class="content-z">
            <h2>Evidence-Backed Reasoning</h2>
            <p>No hallucinations. The verdict is always grounded in the retrieved sources.</p>
            
            <img src="{img2_b64}" class="app-screenshot" alt="TruthSeeker Reasoning" />
            
            <div style="margin-top: 20px;">
                <p style="color: var(--text-main); font-size: 28px;">The LLM provides a concise reasoning paragraph explaining exactly <i>why</i> it reached the verdict, backed by expandable source links.</p>
            </div>
        </div>
        <div class="footer">
            <p>TruthSeeker In Action</p>
            <p>Swipe ➔</p>
        </div>
    </div>

    <!-- SLIDE 6: Agent Routing Log -->
    <div class="slide">
        <div class="glow-blob" style="width: 600px; height: 600px; background: rgba(192, 132, 252, 0.15); top: 30%; left: 20%;"></div>
        
        <div class="content-z">
            <h2>Agent Routing Log</h2>
            <p>Complete transparency into the CRAG decision-making process.</p>
            
            <img src="{img3_b64}" class="app-screenshot" alt="TruthSeeker Routing Path" />
            
            <div class="glass-card" style="padding: 30px; margin-top: 10px;">
                <p style="color: var(--text-main); font-size: 26px; margin: 0;">Notice how the LLM graded the database documents, found <b>0/5 relevant</b>, and successfully triggered the <b>Tavily Web Search</b> fallback node to find the real answer.</p>
            </div>
        </div>
        <div class="footer">
            <p>TruthSeeker In Action</p>
            <p>Swipe ➔</p>
        </div>
    </div>

    <!-- SLIDE 7: Tech Stack & CTA -->
    <div class="slide">
        <div class="glow-blob" style="width: 600px; height: 600px; background: var(--accent-2); top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.2;"></div>
        
        <div class="content-z" style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
            <h2 style="text-align: center; margin-bottom: 80px;">The Stack</h2>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-bottom: 80px;">
                <div class="glass-card" style="margin: 0; padding: 40px;">
                    <h3 style="font-size: 32px; color: var(--text-main);">Brain</h3>
                    <ul style="margin-top: 20px;">
                        <li style="font-size: 24px;">LangGraph</li>
                        <li style="font-size: 24px;">Llama 3.3 70B (Groq)</li>
                        <li style="font-size: 24px;">SentenceTransformers</li>
                    </ul>
                </div>
                <div class="glass-card" style="margin: 0; padding: 40px;">
                    <h3 style="font-size: 32px; color: var(--text-main);">Data & UI</h3>
                    <ul style="margin-top: 20px;">
                        <li style="font-size: 24px;">Supabase (pgvector)</li>
                        <li style="font-size: 24px;">Tavily API (Web Search)</li>
                        <li style="font-size: 24px;">Streamlit</li>
                    </ul>
                </div>
            </div>

            <div style="text-align: center; margin-top: 40px;">
                <h3 style="font-size: 48px; color: var(--text-main); margin-bottom: 20px;">What claim would you check first?</h3>
                <p style="font-size: 32px;">Drop it in the comments below 👇</p>
                <div class="code-block" style="display: inline-block; margin-top: 20px;">
                    github.com/hassanali241/truthseeker
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p style="color: var(--text-main); font-weight: 600;">Hassan Ali</p>
            <p>End of presentation</p>
        </div>
    </div>

</body>
</html>
"""

async def generate_pdf():
    print("Launching Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Loading HTML content...")
        await page.set_content(html_content, wait_until="networkidle")
        
        # Give fonts and images a moment to render properly
        await page.wait_for_timeout(3000)
        
        print("Exporting to PDF...")
        # 1080px by 1350px at 96 DPI is 11.25in x 14.0625in
        await page.pdf(
            path="docs/TruthSeeker_LinkedIn_Beautiful.pdf",
            width="11.25in",
            height="14.0625in",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        await browser.close()
        print("DONE: Beautiful PDF generated: docs/TruthSeeker_LinkedIn_Beautiful.pdf")

if __name__ == "__main__":
    asyncio.run(generate_pdf())
