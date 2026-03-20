import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM


def main() -> None:
    load_dotenv()
    # Start fresh each run so logs are overwritten, not appended.
    with open("output.txt", "w", encoding="utf-8") as file:
        file.write("")

    llm = LLM(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )

    topic = "Which marketing strategy is most suitable for an online clothes shop to increase traffic and sales?"
    researcher = Agent(
        role="Market Researcher",
        goal=(
            "Research common ecommerce marketing strategies and produce practical insights "
            "for a small online clothes shop."
        ),
        backstory=(
            "You are an ecommerce-focused researcher with strong knowledge of online retail growth. "
            "You identify widely used marketing strategies, explain them clearly, and focus on what "
            "is realistically useful for online clothing stores."
        ),
        verbose=True,
        llm=llm,
    )

    analyst = Agent(
        role="Marketing Analyst",
        goal=(
            "Compare major marketing strategy options and choose the single best one for "
            "an online clothes shop using cost, speed, scalability, expected ROI, and suitability."
        ),
        backstory=(
            "You are a practical business analyst with experience advising small online retailers. "
            "You focus on decisions that can be executed with limited budget and team size, and you "
            "justify recommendations with clear trade-offs."
        ),
        verbose=True,
        llm=llm,
    )

    writer = Agent(
        role="Strategy Writer",
        goal=(
            "Produce a clear final business report that presents one recommended strategy, "
            "rationale, a simple 30/60/90-day action plan, risks, and measurable KPIs."
        ),
        backstory=(
            "You are a professional business writer who converts analysis into clean, decision-ready "
            "reports for founders and managers. Your writing is concise, structured, and action-oriented."
        ),
        verbose=True,
        llm=llm,
    )

    research_task = Task(
        description=(
            "Research online marketing strategies for ecommerce clothing stores.\n"
            f"Topic: {topic}\n\n"
            "Your job:\n"
            "1) Identify common ecommerce marketing strategies.\n"
            "2) Briefly explain how each strategy works.\n"
            "3) Focus on strategies relevant to a small online clothes shop.\n"
            "4) Keep output factual and concise."
        ),
        expected_output=(
            "Structured strategy notes in this format:\n"
            "- Strategy Name\n"
            "- Brief Explanation (2-4 sentences)\n"
            "- Relevance to Online Clothes Shop (1-2 sentences)\n"
            "- Practical Use Example (1 sentence)\n"
            "Cover at least 5 common ecommerce marketing strategies and finish with a short synthesis."
        ),
        agent=researcher,
    )

    analysis_task = Task(
        description=(
            "Analyze the research notes from Task 1 and compare possible marketing strategies.\n"
            "Use these criteria: cost, speed to implement, scalability, expected ROI, and suitability "
            "for a small online fashion shop.\n"
            "Choose one best strategy and justify the decision with clear trade-offs."
        ),
        expected_output=(
            "A comparison section that includes:\n"
            "- Comparison table or clear bullet comparison\n"
            "- Pros and cons for each major strategy option\n"
            "- One final chosen strategy with explicit justification tied to the criteria"
        ),
        agent=analyst,
        context=[research_task],
    )

    writing_task = Task(
        description=(
            "Create the final business report using the analysis from Task 2.\n"
            "The report is for an online clothes shop owner who needs a practical marketing strategy decision."
        ),
        expected_output=(
            "Final report in clear sections:\n"
            "1) Report title\n"
            "2) Brief business context (online clothes shop)\n"
            "3) Condensed summary of researched strategies\n"
            "4) Strategy comparison highlights\n"
            "5) Recommended strategy (single clear choice)\n"
            "6) Why this strategy is best\n"
            "7) 30/60/90-day implementation outline\n"
            "8) Risks and mitigation\n"
            "9) Expected outcomes + KPIs (traffic growth, conversion rate, CAC, repeat purchase rate)\n"
            "10) Conclusion"
        ),
        agent=writer,
        context=[analysis_task],
    )

    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=[research_task, analysis_task, writing_task],
        process=Process.sequential,
        verbose=True,
        output_log_file="output.txt",
    )

    result = crew.kickoff(inputs={"topic": topic})
    print(result)
    with open("output.txt", "a", encoding="utf-8") as file:
        file.write("\n\n=== FINAL RESULT ===\n")
        file.write(str(result))
        file.write("\n")


if __name__ == "__main__":
    main()
