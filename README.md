# CrewAI Marketing Strategy Project

This project uses CrewAI to answer the business question: **Which marketing strategy is most suitable for an online clothes shop to increase traffic and sales?**  
The implementation is in `crew.py`, dependencies are listed in `requirements.txt`, and run logs plus final results are written to `output.txt`.

## Business Problem

The project addresses a common challenge for small online fashion businesses: choosing one practical marketing strategy from many options. Online clothes shops usually have limited budget, limited team capacity, and high competition. A poor strategy choice can waste ad spend and delay growth.  
This crew is designed to generate a structured recommendation that balances cost, speed, scalability, expected ROI, and fit for a small ecommerce clothing store.

## How the 3 Agents Work Together

The crew runs in a **sequential** process with three agents and linked tasks in `crew.py`. The **Market Researcher** first identifies and explains common ecommerce marketing strategies relevant to online clothing stores. The **Marketing Analyst** then takes that research context, compares strategy options using clear business criteria, and selects the most suitable strategy with justification. Finally, the **Strategy Writer** uses the analysis context to produce a decision-ready business report with recommendation, rationale, implementation steps, risk/mitigation, and KPIs. This task-by-task context passing makes the final output more coherent and consistent than isolated single-step prompting.

## Challenges Encountered and How They Were Solved

1. **Environment stability and Python version alignment**  
   During development, the virtual environment was switched across Python versions to match project requirements. Recreating the `venv` and reinstalling from `requirements.txt` ensured dependency consistency and avoided runtime mismatch issues.

2. **Output logging requirements**  
   A key requirement was that `output.txt` include not only the final answer but also full crew execution details. This was solved by configuring CrewAI logging to `output_log_file="output.txt"` and ensuring the file is reset at the start of each run, then appending a clear final-result section.

3. **Keeping implementation simple while meeting assignment constraints**  
   The project went through iterations (including scraping-based approaches), but was refined to an LLM-only research workflow to stay simple, readable, and aligned with the required structure (3 agents, 3 tasks, sequential process, context passing).

## One Thing I Would Change with More Time

If I had more time, I would add an evaluation layer for output quality and reliability: for example, a lightweight validation step that scores the final recommendation against a rubric (clarity, feasibility, KPI quality, and risk coverage). This would make results more consistent across multiple runs and easier to compare for grading or business decision-making.

## Project Files

- `crew.py`: Main CrewAI implementation (agents, tasks, sequential crew execution)
- `requirements.txt`: Python dependencies
- `output.txt`: Full execution log and final result
