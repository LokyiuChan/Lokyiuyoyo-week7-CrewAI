# CrewAI Marketing Strategy Assistant

## Project Overview
This project uses a CrewAI workflow to answer the business question:

**Which marketing strategy is most suitable for an online clothes shop to increase traffic and sales?**

The implementation is in `crew.py`, dependencies are listed in `requirements.txt`, and execution logs plus final results are written to `output.txt`.

## Business Problem
Small online clothes shops often have limited budget and time, but many possible marketing channels (social ads, SEO, influencer marketing, email, etc.). Choosing the wrong strategy can waste money and slow growth. This crew helps by researching options, comparing them with practical criteria, and delivering one clear recommendation with action steps and KPIs.

## How the 3 Agents Work Together
The crew runs in a **sequential** process with three agents in `crew.py`. First, the **Market Researcher** identifies and explains three relevant strategies for a small online clothes shop. Next, the **Marketing Analyst** compares those strategies using cost, ease of implementation, and sales potential, then selects one best option. Finally, the **Strategy Writer** turns the analysis into a short, decision-ready report that includes the recommended strategy, why it is best, a simple action plan, and KPIs. Each task uses the previous task's output as context, so the final recommendation is structured and consistent.

## Challenges Encountered and Solutions
- **Challenge:** Intermittent DeepSeek connection failure:  
  `litellm.InternalServerError: DeepseekException - peer closed connection without sending complete message body (incomplete chunked read)`
- **Likely Cause:** Prompts/tasks were too long and generated large responses, increasing request instability.
- **Solution Implemented:**
  - Simplified task scope and output requirements (exactly 3 strategies, concise sections, no long paragraphs).
  - Kept outputs short and structured with bullets to reduce response size.
  - Captured full runtime console output into `output.txt` to improve debugging and traceability (agent logs, errors, and final result).

## What I Would Change With More Time
If I had more time, I would add a lightweight evaluation loop that runs the crew with multiple prompt variants and scores outputs (clarity, actionability, and KPI quality), then automatically keeps the best result. This would improve recommendation quality and consistency without making the core workflow more complex.

## How to Run
1. Activate your virtual environment.
2. Ensure `.env` contains valid DeepSeek settings.
3. Run:

```bash
python crew.py
```

After execution, check `output.txt` for full logs and the final report.
