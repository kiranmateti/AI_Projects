import os
import logging

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

logger = logging.getLogger(__name__)
app = FastAPI(title="Agno Architect-Developer-Tester API")


class PipelineRequest(BaseModel):
    prompt: str = Field(min_length=1, description="Task for the Architect agent")


class PipelineResponse(BaseModel):
    architecture: str
    development: str
    testing: str


def run_agent(agent: Agent, agent_name: str, task: str) -> str:
    print(f"[{agent_name}] Status: IN_PROGRESS", flush=True)
    try:
        response = agent.run(task)
        output = response.content
        if output is None or not str(output).strip():
            raise RuntimeError(f"{agent_name} returned an empty response.")
    except Exception:
        print(f"[{agent_name}] Status: FAILED", flush=True)
        raise

    result = str(output)
    print(f"[{agent_name}] Status: COMPLETED", flush=True)
    print(f"\n--- {agent_name} output ---\n{result}\n", flush=True)
    return result


def run_pipeline(
    user_prompt: str,
    architect: Agent,
    developer: Agent,
    tester: Agent,
) -> tuple[str, str, str]:

    architecture = run_agent(
        architect,
        "Architect",
        f"""Design a clear, practical architecture for this request.
Identify key components, responsibilities, data flow, and important decisions.

User request:
{user_prompt}""",
    )

    development = run_agent(
        developer,
        "Developer",
        f"""Develop an implementation approach for the user's request.
Follow the architecture below. Point out any assumptions and provide concrete
implementation details.

User request:
{user_prompt}

Architect's output:
{architecture}""",
    )

    testing = run_agent(
        tester,
        "Tester",
        f"""Create a focused test plan for the requested implementation. Cover
normal behavior, edge cases, and failure handling. Evaluate the developer's
approach against the architecture and call out any gaps.

User request:
{user_prompt}

Architect's output:
{architecture}

Developer's output:
{development}""",
    )
    return architecture, development, testing


def create_agent(
    name: str,
    role_instructions: str,
    base_url: str,
    api_key: str,
    model_id: str,
) -> Agent:
    return Agent(
        name=name,
        model=OpenAIChat(id=model_id, base_url=base_url, api_key=api_key),
        tools=[DuckDuckGoTools()],
        instructions=[role_instructions],
    )


@app.post("/run", response_model=PipelineResponse)
def run_agents(request: PipelineRequest) -> PipelineResponse:
    user_prompt = request.prompt.strip()
    if not user_prompt:
        raise HTTPException(status_code=422, detail="The prompt cannot be empty.")

    base_url = os.getenv("BASE_URL")
    api_key = os.getenv("API_KEY")
    model_id = os.getenv("MODEL")
    if not all((base_url, api_key, model_id)):
        raise HTTPException(
            status_code=503,
            detail="BASE_URL, API_KEY, and MODEL must be configured.",
        )

    architect = create_agent(
        "Architect",
        "You are a software architect. Produce a structured, actionable design. "
        "Use web search when current information or external references are useful.",
        base_url,
        api_key,
        model_id,
    )
    developer = create_agent(
        "Developer",
        "You are a senior software developer. Turn the provided design into a "
        "concrete implementation approach. Use web search when current "
        "information or external references are useful.",
        base_url,
        api_key,
        model_id,
    )
    tester = create_agent(
        "Tester",
        "You are a thorough software tester. Review the supplied design and "
        "implementation approach, then provide a practical test plan. Use web "
        "search when current information or external references are useful.",
        base_url,
        api_key,
        model_id,
    )

    try:
        architecture, development, testing = run_pipeline(
            user_prompt, architect, developer, tester
        )
    except Exception as exc:
        logger.exception("Agent pipeline failed")
        raise HTTPException(
            status_code=502, detail="An agent failed while processing the task."
        ) from exc
    return PipelineResponse(
        architecture=architecture,
        development=development,
        testing=testing,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
