"""
Visionary Video Generator — Automated YouTube Shorts / TikTok Creator
Pipeline: Topic → Script → Voiceover → Background → Captions → Final Video
Uses: edge-tts (free), ffmpeg, Pillow, Qwen via OpenRouter
"""

import os
import sys
import json
import random
import subprocess
import tempfile
import shutil
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────────────────
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/root/sites/video-generator/output")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
BG_COLOR = (13, 27, 42)        # Dark navy
ACCENT_COLOR = (44, 177, 188)  # Teal
TEXT_COLOR = (226, 234, 243)   # Light
MUTED_COLOR = (138, 165, 191) # Muted

NICHES = {
    "debt": {
        "hooks": [
            "Stop paying minimums on your credit cards. Here's why.",
            "Your debt is costing you $XXX/month in interest alone.",
            "I'm going to show you the fastest way out of debt.",
            "Nobody tells you this about credit card debt.",
            "If you have debt, you need to hear this.",
        ],
        "topics": [
            "snowball vs avalanche debt payoff which is better",
            "how to pay off credit cards when you're broke",
            "the minimum payment trap how credit cards keep you poor",
            "why your debt feels impossible and what to do",
            "how I would pay off 10k in credit card debt fast",
            "the hybrid debt method nobody talks about",
            "saving money while paying off debt yes its possible",
            "emergency fund vs debt payoff the right answer",
        ],
        "cta": "Try our free AI debt coach — link in bio",
    },
    "investing": {
        "hooks": [
            "You're losing money every day you don't invest. Here's why.",
            "Investing isn't just for rich people. Let me explain.",
            "If you saved $5/day starting now, here's what you'd have.",
            "The single biggest investing mistake beginners make.",
        ],
        "topics": [
            "why you need to start investing today not tomorrow",
            "compound interest the eighth wonder of the world explained",
            "index funds explained the simplest way to invest",
            "how to start investing with just 50 dollars",
            "the difference between saving and investing",
            "what is an ETF and why should you care",
            "how inflation silently steals your money if you dont invest",
            "dollar cost averaging the boring strategy that works",
        ],
        "cta": "Get your financial plan free — link in bio",
    },
    "motivation": {
        "hooks": [
            "You're closer to debt freedom than you think.",
            "This is your sign to take control of your money.",
            "Someone paid off 50k in debt. Here's how they did it.",
            "You don't need to be rich to start. You need to start.",
        ],
        "topics": [
            "from 30k in debt to debt free my real story",
            "the moment I decided to take control of my money",
            "why most people stay broke and how to be different",
            "celebrate small wins on your debt journey heres why",
            "your debt does not define you remember that",
            "the 30 day money challenge that changed everything",
        ],
        "cta": "Start your free debt plan today — link in bio",
    },
    "tool_demo": {
        "hooks": [
            "Watch this AI build a debt payoff plan in 30 seconds.",
            "This free tool does what financial advisors charge for.",
            "I built an AI that helps you get out of debt. Try it.",
        ],
        "topics": [
            "how Nova AI builds your personalized debt payoff plan",
            "watch me get a debt snowball plan in 30 seconds free",
            "Nova AI vs financial advisor which is better for debt",
            "how to use Nova to track your debt payoff progress",
        ],
        "cta": "Try Nova free right now — link in bio",
    },
        "hooks": [
            "Stop paying minimums on your credit cards. Here's why.",
            "Your debt is costing you $XXX/month in interest alone.",
            "I'm going to show you the fastest way out of debt.",
            "Nobody tells you this about credit card debt.",
            "If you have debt, you need to hear this.",
        ],
        "topics": [
            "snowball vs avalanche debt payoff which is better",
            "how to pay off credit cards when you're broke",
            "the minimum payment trap how credit cards keep you poor",
            "why your debt feels impossible and what to do",
            "how I would pay off 10k in credit card debt fast",
            "the hybrid debt method nobody talks about",
            "saving money while paying off debt yes its possible",
            "emergency fund vs debt payoff the right answer",
        ],
        "cta": "Try our free AI debt coach — link in bio",
    },
    "finance_tips": {
        "hooks": [
            "3 money mistakes that keep you broke.",
            "Rich people do this with their money. You don't.",
            "Stop doing this with your paycheck right now.",
        ],
        "topics": [
            "the 50 30 20 budget rule explained simply",
            "how to find 200 extra dollars this month",
            "subscription audit find hidden money leaks",
            "meal prep saves 300 a month heres how",
        ],
        "cta": "Free debt payoff plan — link in bio",
    }
}

# ─── LLM Script Generation ───────────────────────────────────────────────
def generate_script(niche: str, topic: str, hook: str, cta: str) -> dict:
    """Generate a short-form video script using Qwen."""
    if not OPENROUTER_KEY:
        return fallback_script(topic, hook, cta)

    import httpx
    prompt = f"""You are a viral short-form video script writer for TikTok and YouTube Shorts.
Niche: {niche}
Topic: {topic}
Hook: {hook}
Call to action: {cta}

Write a script that:
1. Starts with the hook (grab attention in first 3 seconds)
2. Delivers value fast (30-45 seconds of content)
3. Ends with the CTA
4. Uses short punchy sentences
5. No filler words
6. Sounds like a real person talking, not AI
7. Total length: 45-60 seconds when read aloud

Return JSON: {{"title": "...", "script": "...", "hashtags": ["..."]}}"""

    try:
        r = httpx.post("https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://visionary-consultant.pages.dev",
            },
            json={
                "model": "qwen/qwen3.6-plus",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
            },
            timeout=30,
        )
        data = r.json()
        if "error" in data:
            print(f"  LLM API error: {data['error']}")
            return fallback_script(topic, hook, cta, niche)
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not text:
            print(f"  LLM returned empty response")
            return fallback_script(topic, hook, cta, niche)
        # Extract JSON from response
        if "{" in text and "}" in text:
            start = text.index("{")
            end = text.rindex("}") + 1
            result = json.loads(text[start:end])
            return result
        # No JSON found, wrap the text as script
        return {"title": topic.replace("_", " ").title(), "script": text, "hashtags": ["#debt", "#money", "#finance"]}
    except Exception as e:
        print(f"  LLM error: {e}, using fallback")

    return fallback_script(topic, hook, cta)


FALLBACK_SCRIPTS = {
    "debt": [
        {
            "title": "The Minimum Payment Trap",
            "script": "Nobody tells you this about credit card debt. When you only pay the minimum, you're not paying off your balance. You're just renting the debt. On a five thousand dollar card at twenty two percent APR, minimum only means you pay it off in eighteen years. Eighteen years! And you'll pay over seven grand in interest. More than the original debt. Here's the move. Pay just fifty bucks extra a month. That eighteen years becomes four. You save five thousand dollars in interest. Fifty dollars. That's it. Try our free AI debt coach and get your exact payoff plan.",
            "hashtags": ["#debt", "#creditcards", "#money", "#debtfree", "#personalfinance"],
        },
        {
            "title": "Snowball vs Avalanche Which Is Right For You",
            "script": "Two ways to pay off debt. Snowball and Avalanche. Snowball means smallest balance first. You get quick wins. Feels amazing. Avalanche means highest interest first. Saves the most money. Feels slow. Which one wins? If you have high interest debt above twenty percent, go Avalanche. The math is too big to ignore. But if you keep quitting plans, go Snowball. Momentum beats math when you're overwhelmed. Or do what smart people do. Start with one small win. Then switch to Avalanche. Best of both worlds. Get your free personalized plan with our AI debt coach.",
            "hashtags": ["#debtsnowball", "#debtavalanche", "#debt", "#money", "#personalfinance"],
        },
        {
            "title": "You Can Save Money While Paying Off Debt",
            "script": "Everyone says you can't save while paying off debt. Wrong. Here's the trick. Take just ten percent of your extra payment and put it in savings. If you pay four hundred extra, that's forty bucks to savings. Three sixty to debt. Why? Because life happens. Car breaks down. Medical bill shows up. Without savings, you go right back into debt. Every single time. Build a cushion while you destroy the debt. Our AI coach sets this up automatically. Try it free.",
            "hashtags": ["#savings", "#debt", "#emergencyfund", "#money", "#personalfinance"],
        },
        {
            "title": "3 Things Your Credit Card Company Won't Tell You",
            "script": "First. Minimum payments are designed to keep you in debt forever. Literally. They set the minimum so you never pay it off. Second. If you miss one payment, your interest rate can jump to twenty nine percent. One mistake. Double the cost. Third. Balance transfer cards sound great. Zero percent for twelve months. But if you don't pay it all off in time, the rate jumps to twenty five percent retroactively. Know the game. Play it smarter. Get your free debt payoff plan now.",
            "hashtags": ["#creditcards", "#debt", "#moneytips", "#finance", "#personalfinance"],
        },
    ],
    "finance_tips": [
        {
            "title": "Find Two Hundred Dollars This Month",
            "script": "You have hidden money. You just don't know it. Here's where. One. Audit your subscriptions. Most people have fifty to one fifty a month in forgotten charges. Two. Meal prep on Sunday. Saves the average person two hundred to four hundred a month on takeout. Three. Call your insurance company. Ask for a better rate. Works thirty percent of the time. That's potentially four hundred extra dollars a month toward your debt or savings. Small moves. Big results. Get your free personalized plan.",
            "hashtags": ["#moneytips", "#budget", "#savings", "#finance", "#personalfinance"],
        },
    ],
}

FALLBACK_SCRIPTS["investing"] = [
    {
        "title": "Compound Interest Will Make You Rich",
        "script": "You're losing money every day you don't invest. Here's why. Compound interest means your money earns money. Then that money earns money. It snowballs. If you invest two hundred a month starting at twenty five, you'll have over a million dollars by sixty five. A million. From two hundred bucks a month. But if you wait until thirty five? Three hundred and fifty thousand. You lose six hundred grand by waiting ten years. That's the cost of waiting. Start now. Even fifty bucks a month. Just start. Get your free financial plan with our AI coach.",
        "hashtags": ["#investing", "#compoundinterest", "#money", "#finance", "#personalfinance"],
    },
    {
        "title": "Index Funds Are All You Need",
        "script": "Investing sounds complicated. It's not. Index funds are the simplest way to build wealth. You buy one fund. It holds hundreds of stocks. Low fees. Automatic diversification. Historically returns about ten percent a year. You don't need to pick stocks. You don't need a financial advisor. You need an S and P five hundred index fund and time. That's it. Set up automatic contributions. Forget about it. Come back in twenty years. You're welcome. Start your investing journey with our free AI coach.",
        "hashtags": ["#indexfunds", "#investing", "#stocks", "#finance", "#personalfinance"],
    },
]
FALLBACK_SCRIPTS["motivation"] = [
    {
        "title": "You're Closer Than You Think",
        "script": "You're closer to debt freedom than you think. I know it feels impossible right now. The numbers. The stress. The calls. But listen. Every dollar you pay off is a dollar that's gone forever. It adds up faster than you realize. Someone I know paid off thirty thousand in two years making forty five thousand a year. Not magic. Just a plan and consistency. You can do this. You just need to start. Right now. Today. Not Monday. Not next month. Today. Our AI coach will build you a free plan. Try it.",
        "hashtags": ["#debtfree", "#motivation", "#money", "#debtfreedom", "#personalfinance"],
    },
]
FALLBACK_SCRIPTS["tool_demo"] = [
    {
        "title": "Watch Nova Build a Debt Plan in 30 Seconds",
        "script": "Watch this AI build a debt payoff plan in thirty seconds. You type in your debts. Credit card. Car loan. Student loan. Nova analyzes your balances, rates, and income. Then it generates a personalized payoff plan. Snowball. Avalanche. Or hybrid. Your choice. It shows you exactly when you'll be debt free. Down to the month. It even calculates how much interest you'll save. All free. No signup required. Just type and get your plan. Try Nova now. Link in bio.",
        "hashtags": ["#AI", "#debt", "#fintech", "#personalfinance", "#debtfree"],
    },
]

def fallback_script(topic: str, hook: str, cta: str, niche: str = "debt") -> dict:
    """Fallback script when LLM is unavailable."""
    scripts = FALLBACK_SCRIPTS.get(niche, FALLBACK_SCRIPTS["debt"])
    return random.choice(scripts)


# ─── Voiceover ────────────────────────────────────────────────────────────
async def generate_voiceover(text: str, output_path: str, voice: str = "en-US-GuyNeural") -> float:
    """Generate TTS voiceover using edge-tts (free)."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

    # Get duration using ffprobe
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", output_path],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


# ─── Background Frames ────────────────────────────────────────────────────
def generate_frame(text_line: str, frame_num: int, total_frames: int,
                   subtitle: str = "", output_dir: str = "") -> str:
    """Generate a single video frame with text overlay using Pillow."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Accent line at top
    draw.rectangle([0, 0, VIDEO_WIDTH, 8], fill=ACCENT_COLOR)

    # Logo area
    try:
        font_large = ImageFont.truetype(FONT_PATH, 52)
        font_medium = ImageFont.truetype(FONT_PATH, 38)
        font_small = ImageFont.truetype(FONT_PATH, 30)
        font_brand = ImageFont.truetype(FONT_PATH, 26)
    except Exception:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
        font_brand = font_small

    # Main text (word-wrapped, centered)
    max_chars_per_line = 28
    words = text_line.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) <= max_chars_per_line:
            current_line = (current_line + " " + word).strip()
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    y_start = 500 - (len(lines) * 60)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        x = (VIDEO_WIDTH - bbox[2] + bbox[0]) // 2
        draw.text((x, y_start), line, fill=TEXT_COLOR, font=font_large)
        y_start += 70

    # Subtitle
    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=font_small)
        x = (VIDEO_WIDTH - bbox[2] + bbox[0]) // 2
        draw.text((x, 1100), subtitle, fill=MUTED_COLOR, font=font_small)

    # Brand - Nova Debt AI
    try:
        logo_path = "/root/sites/visionary-consultant/brand/nova-icon.svg"
        if os.path.exists(logo_path):
            # SVG can't be loaded directly by Pillow, skip to text branding
            pass
    except Exception:
        pass
    draw.text((40, VIDEO_HEIGHT - 120), "🤖 Nova Debt AI", fill=ACCENT_COLOR, font=font_brand)
    draw.text((40, VIDEO_HEIGHT - 80), "visionary-consultant.pages.dev", fill=MUTED_COLOR, font=font_brand)

    # Progress bar
    progress = frame_num / max(total_frames, 1)
    bar_width = int(VIDEO_WIDTH * 0.8)
    bar_x = (VIDEO_WIDTH - bar_width) // 2
    draw.rectangle([bar_x, 1800, bar_x + bar_width, 1810], fill=(42, 63, 85))
    draw.rectangle([bar_x, 1800, bar_x + int(bar_width * progress), 1810], fill=ACCENT_COLOR)

    path = os.path.join(output_dir, f"frame_{frame_num:05d}.png")
    img.save(path)
    return path


# ─── Assemble Video ────────────────────────────────────────────────────────
def assemble_video(audio_path: str, script_text: str, output_path: str, title: str = ""):
    """Assemble final video from audio + generated frames."""
    # Get audio duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True,
    )
    duration = float(result.stdout.strip())
    total_frames = int(duration * FPS)

    # Split script into segments for frame generation
    sentences = [s.strip() for s in script_text.replace(".", ".|").replace("!", "!|").replace("?", "?|").split("|") if s.strip()]
    frames_per_segment = max(1, total_frames // max(len(sentences), 1))

    with tempfile.TemporaryDirectory() as tmpdir:
        # Generate frames
        print(f"  Generating {total_frames} frames...")
        frame_dir = os.path.join(tmpdir, "frames")
        os.makedirs(frame_dir)

        frame_num = 0
        for seg_idx, sentence in enumerate(sentences):
            seg_frames = frames_per_segment if seg_idx < len(sentences) - 1 else (total_frames - frame_num)
            subtitle = ""
            for i in range(seg_frames):
                if frame_num >= total_frames:
                    break
                generate_frame(sentence, frame_num, total_frames, subtitle, frame_dir)
                frame_num += 1

        # Use ffmpeg to combine frames + audio
        print(f"  Assembling video with ffmpeg...")
        frames_pattern = os.path.join(frame_dir, "frame_%05d.png")
        subprocess.run([
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", frames_pattern,
            "-i", audio_path,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            "-movflags", "+faststart",
            output_path,
        ], capture_output=True, check=True)

    print(f"  ✅ Video saved: {output_path}")
    return output_path


# ─── Main Pipeline ────────────────────────────────────────────────────────
async def generate_video(niche: str = "debt", topic: str = None, voice: str = "en-US-GuyNeural"):
    """Full pipeline: topic → script → voiceover → video."""
    niche_data = NICHES.get(niche, NICHES["debt"])
    topic = topic or random.choice(niche_data["topics"])
    hook = random.choice(niche_data["hooks"])
    cta = niche_data["cta"]

    print(f"🎬 Generating video for: {topic}")

    # Step 1: Generate script
    print("  Step 1: Generating script...")
    script_data = generate_script(niche, topic, hook, cta)
    title = script_data.get("title", topic)
    script_text = script_data.get("script", "")
    hashtags = script_data.get("hashtags", [])
    print(f"  Title: {title}")
    print(f"  Script: {script_text[:100]}...")

    # Step 2: Generate voiceover
    print("  Step 2: Generating voiceover...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_title = "".join(c if c.isalnum() else "_" for c in title)[:40]
    audio_path = os.path.join(OUTPUT_DIR, f"{safe_title}_audio.mp3")
    video_path = os.path.join(OUTPUT_DIR, f"{safe_title}.mp4")

    duration = await generate_voiceover(script_text, audio_path, voice)
    print(f"  Audio duration: {duration:.1f}s")

    # Step 3: Assemble video
    print("  Step 3: Assembling video...")
    assemble_video(audio_path, script_text, video_path, title)

    # Step 4: Generate caption file
    caption = f"{script_text}\n\n{' '.join(hashtags)}"
    caption_path = os.path.join(OUTPUT_DIR, f"{safe_title}_caption.txt")
    with open(caption_path, "w") as f:
        f.write(caption)

    print(f"\n✨ Done! Files:")
    print(f"  Video: {video_path}")
    print(f"  Audio: {audio_path}")
    print(f"  Caption: {caption_path}")

    return {
        "title": title,
        "script": script_text,
        "hashtags": hashtags,
        "video_path": video_path,
        "audio_path": audio_path,
        "caption_path": caption_path,
        "duration": duration,
    }


# ─── CLI ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio

    niche = sys.argv[1] if len(sys.argv) > 1 else "debt"
    topic = sys.argv[2] if len(sys.argv) > 2 else None
    voice = sys.argv[3] if len(sys.argv) > 3 else "en-US-GuyNeural"

    result = asyncio.run(generate_video(niche, topic, voice))
    print(json.dumps(result, indent=2, default=str))
