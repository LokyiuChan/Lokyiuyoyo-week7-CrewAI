import os
import sys
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM


class TeeStream:
    def __init__(self, console_stream, log_stream) -> None:
        self.console_stream = console_stream
        self.log_stream = log_stream

    def write(self, data: str) -> int:
        self.console_stream.write(data)
        self.log_stream.write(data)
        self.log_stream.flush()
        return len(data)

    def flush(self) -> None:
        self.console_stream.flush()
        self.log_stream.flush()


def main() -> None:
    load_dotenv(override=True)

    llm = LLM(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        timeout=120,
        max_retries=2,
    )

    topic = "Which marketing strategy is most suitable for an online clothes shop to increase traffic and sales?"
    researcher = Agent(
        role="Market Researcher",
        goal=(
            "Research a small set of practical ecommerce marketing strategies "
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
            "Compare three strategy options and choose one best strategy for "
            "an online clothes shop using simple decision criteria."
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
            "Produce a short final business report with one recommendation, "
            "brief reasoning, a simple action plan, and KPIs."
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
            "1) Identify exactly 3 marketing strategies.\n"
            "2) For each strategy, include:\n"
            "   - name\n"
            "   - 2-3 sentence explanation\n"
            "   - 3-4 sentence why it is useful for a small online clothes shop\n"
            "3) Keep writing concise and avoid long paragraphs."
        ),
        expected_output=(
            "A concise list of exactly 3 strategies in this format for each:\n"
            "- Name\n"
            "- Explanation (2-3 sentences)\n"
            "- Why Useful (3-4 sentences)\n"
            "Use short sentences and compact bullet points only."
        ),
        agent=researcher,
    )

    analysis_task = Task(
        description=(
            "Analyze the 3 strategies from Task 1.\n"
            "Compare them using only these criteria:\n"
            "- cost\n"
            "- ease of implementation\n"
            "- sales potential\n"
            "Choose ONE best strategy.\n"
            "Keep output concise and avoid long paragraphs."
        ),
        expected_output=(
            "A concise comparison with:\n"
            "- A short table or bullet comparison across the 3 criteria\n"
            "- ONE final selected strategy\n"
            "- Brief reason for the selection"
        ),
        agent=analyst,
        context=[research_task],
    )

    writing_task = Task(
        description=(
            "Create a short final report based on Task 2 for an online clothes shop owner.\n"
            "Use concise bullets and short sentences only.\n"
            "Do not include long paragraphs."
        ),
        expected_output=(
            "Final report with only these sections:\n"
            "1) Recommended strategy\n"
            "2) Why it is best\n"
            "3) Simple action plan\n"
            "4) KPIs\n"
            "Keep each section brief and practical."
        ),
        agent=writer,
        context=[analysis_task],
    )

    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=[research_task, analysis_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )
    with open("output.txt", "w", encoding="utf-8") as log_file:
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = TeeStream(original_stdout, log_file)
        sys.stderr = TeeStream(original_stderr, log_file)
        try:
            result = crew.kickoff(inputs={"topic": "marketing strategy"})
            final_text = str(result)
            print(final_text)
        except Exception as err:
            print(f"Crew execution failed: {err}")
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr


if __name__ == "__main__":
    main()
import os
import sys
import time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM


class _TeeStream:
    """Write output to console and a log file at the same time."""

    def __init__(self, console_stream, log_stream) -> None:
        self.console_stream = console_stream
        self.log_stream = log_stream

    def write(self, data: str) -> int:
        self.console_stream.write(data)
        self.log_stream.write(data)
        self.log_stream.flush()
        return len(data)

    def flush(self) -> None:
        self.console_stream.flush()
        self.log_stream.flush()


def _normalize_model_name(raw_model: str) -> str:
    """Ensure LiteLLM receives provider-prefixed DeepSeek model name."""
    model = (raw_model or "").strip()
    if not model:
        return "deepseek/deepseek-chat"
    if "/" in model:
        return model
    return f"deepseek/{model}"


def _normalize_base_url(raw_base_url: str) -> str:
    """Use a stable OpenAI-compatible DeepSeek endpoint for LiteLLM."""
    base_url = (raw_base_url or "").strip().rstrip("/")
    if not base_url:
        base_url = "https://api.deepseek.com"
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    return base_url


def _is_transient_llm_error(err: Exception) -> bool:
    text = str(err).lower()
    transient_markers = [
        "incomplete chunked read",
        "peer closed connection",
        "connection reset",
        "connection aborted",
        "read timeout",
        "timed out",
        "rate limit",
        "service unavailable",
        "internalservererror",
    ]
    return any(marker in text for marker in transient_markers)


def main() -> None:
    load_dotenv(override=True)
    model_name = _normalize_model_name(os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    base_url = _normalize_base_url(os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"))

    llm = LLM(
        model=model_name,
        base_url=base_url,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        timeout=120,
        max_retries=2,
    )

    topic = "Which marketing strategy is most suitable for an online clothes shop to increase traffic and sales?"
    researcher = Agent(
        role="Market Researcher",
        goal=(
            "Research a small set of practical ecommerce marketing strategies "
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
            "Compare three strategy options and choose one best strategy for "
            "an online clothes shop using simple decision criteria."
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
            "Produce a short final business report with one recommendation, "
            "brief reasoning, a simple action plan, and KPIs."
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
            "1) Identify exactly 3 marketing strategies.\n"
            "2) For each strategy, include:\n"
            "   - name\n"
            "   - 2-3 sentence explanation\n"
            "   - 3-4 sentence why it is useful for a small online clothes shop\n"
            "3) Keep writing concise and avoid long paragraphs."
        ),
        expected_output=(
            "A concise list of exactly 3 strategies in this format for each:\n"
            "- Name\n"
            "- Explanation (2-3 sentences)\n"
            "- Why Useful (3-4 sentences)\n"
            "Use short sentences and compact bullet points only."
        ),
        agent=researcher,
    )

    analysis_task = Task(
        description=(
            "Analyze the 3 strategies from Task 1.\n"
            "Compare them using only these criteria:\n"
            "- cost\n"
            "- ease of implementation\n"
            "- sales potential\n"
            "Choose ONE best strategy.\n"
            "Keep output concise and avoid long paragraphs."
        ),
        expected_output=(
            "A concise comparison with:\n"
            "- A short table or bullet comparison across the 3 criteria\n"
            "- ONE final selected strategy\n"
            "- Brief reason for the selection"
        ),
        agent=analyst,
        context=[research_task],
    )

    writing_task = Task(
        description=(
            "Create a short final report based on Task 2 for an online clothes shop owner.\n"
            "Use concise bullets and short sentences only.\n"
            "Do not include long paragraphs."
        ),
        expected_output=(
            "Final report with only these sections:\n"
            "1) Recommended strategy\n"
            "2) Why it is best\n"
            "3) Simple action plan\n"
            "4) KPIs\n"
            "Keep each section brief and practical."
        ),
        agent=writer,
        context=[analysis_task],
    )

    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=[research_task, analysis_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )

    with open("output.txt", "w", encoding="utf-8") as log_file:
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = _TeeStream(original_stdout, log_file)
        sys.stderr = _TeeStream(original_stderr, log_file)
        try:
            max_attempts = 4
            for attempt in range(1, max_attempts + 1):
                try:
                    result = crew.kickoff(inputs={"topic": "marketing strategy"})
                    final_text = str(result)
                    print(final_text)
                    break
                except Exception as err:
                    is_last_attempt = attempt == max_attempts
                    can_retry = _is_transient_llm_error(err) and not is_last_attempt
                    if can_retry:
                        wait_seconds = 2 ** attempt
                        print(
                            f"Transient LLM error on attempt {attempt}/{max_attempts}: {err}. "
                            f"Retrying in {wait_seconds}s..."
                        )
                        time.sleep(wait_seconds)
                        continue

                    error_message = (
                        f"Crew execution failed after attempt {attempt}/{max_attempts}: {err}"
                    )
                    print(error_message)
                    break
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr


if __name__ == "__main__":
    main()
