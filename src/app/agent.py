from typing import Literal, Dict, Union
from pathlib import Path
import asyncio
import re

from dotenv import load_dotenv
from upsonic import Agent, Task, Graph
import aiofiles


from .tools import FinanceTool
from .constants import STOCK_ANALYST_INST, RESEARCH_ANALYST_INST, INVESTMENT_LEAD_INST


ScenarioType = Literal[
    "AAPL, MSFT, GOOGL",  # Tech Giants
    "NVDA, AMD, INTC",  # Semiconductor Leaders
    "TSLA, F, GM",  # Automotive Innovation
    "JPM, BAC, GS",  # Banking Sector
    "AMZN, WMT, TGT",  # Retail Competition
    "PFE, JNJ, MRNA",  # Healthcare Focus
    "XOM, CVX, BP",  # Energy Sector
]


load_dotenv()


def parse_task_outputs(task_outputs: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """
    Parses a dictionary of task outputs and organizes them into structured sections.

    Args:
        task_outputs: A dictionary where keys are UUIDs and values are markdown-like analysis strings.

    Returns:
        A dictionary where each key maps to structured sections like Market Research, Financial Analysis, etc.
    """
    parsed_results = {}

    for task_id, content in task_outputs.items():
        if not content.strip().startswith("###"):
            continue
        
        section_dict = {}
        sections = re.split(r'### (.*?)\s*[\n\r]+', content)
        

        for i in range(1, len(sections), 2):
            title = sections[i].strip()
            body = sections[i+1].strip()
            section_dict[title] = body

        parsed_results[task_id] = section_dict

    return parsed_results


def format_task_outputs_as_markdown(parsed_outputs: dict) -> str:
    """
    Converts parsed task outputs (nested dict) into clean markdown string.

    Args:
        parsed_outputs (dict): Output of `parse_task_outputs`

    Returns:
        str: Markdown-formatted string
    """
    lines = []
    for task_id, sections in parsed_outputs.items():
        lines.append(f"# Task ID: {task_id}\n")
        for section_title, section_content in sections.items():
            cleaned_title = section_title.strip("# ").strip()
            lines.append(f"## {cleaned_title}\n")
            lines.append(section_content.strip())
            lines.append("")  # newline for spacing
    return "\n".join(lines)



async def write_task_outputs_to_markdown(task_outputs: dict, file_path: Union[str, Path]):
    """
    Parses task_outputs and writes the structured result to a markdown file asynchronously.

    Args:
        task_outputs (dict): The dictionary containing raw task output strings.
        file_path (str or Path): The path to the markdown file where results will be written.
    """
    parsed = parse_task_outputs(task_outputs)
    markdown_content = format_task_outputs_as_markdown(parsed)

    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(markdown_content)


async def agent(query: ScenarioType):
    """
    Main function to run the agent with the provided query.
    Args:
        query: A string representing the scenario type or company names to analyze.
    Returns:
        None
    """
    tool = FinanceTool()


    stock_analyst  = Agent(name="Stock Analyst", model="azure/gpt-4o-mini", debug=True)
    research_analyst = Agent(name="Research Analyst", model="azure/gpt-4o-mini", debug=True)
    investment_lead = Agent(name="Investment Lead", model="azure/gpt-4o-mini", debug=True)


    task_stock_analyst = Task(STOCK_ANALYST_INST + f"Company name: {query}", tools=await tool.get_all_tools(), agent=stock_analyst)
    task_research_analyst = Task(RESEARCH_ANALYST_INST, tools=await tool.get_all_tools(), agent=research_analyst)
    task_investment_lead = Task(INVESTMENT_LEAD_INST, tools=await tool.get_all_tools(), agent=investment_lead)

    graph = Graph(show_progress=True)

    graph.add(task_stock_analyst >> task_research_analyst >> task_investment_lead)
    
    result = await graph.run_async(verbose=True)


    return result


async def main():
    result = await agent("AAPL, MSFT, GOOGL")
    await write_task_outputs_to_markdown(result.task_outputs, "result.md") 

asyncio.run(main())