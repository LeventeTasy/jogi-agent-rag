from crewai import Agent, Crew, Process, Task, Memory
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

load_dotenv()

@CrewBase
class JogiAgent():
    """JogiAgent crew"""

    is_verbose = os.getenv("CREWAI_VERBOSE_ENABLED", "True").lower() == "true"

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

    def get_embedding_function(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            api_key=api_key
        )

    @agent
    def jogi_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['jogi_strategist'],  # type: ignore[index]
            verbose=self.is_verbose,
            temperature=0.1,
            max_retries=5
        )

    @agent
    def jogi_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['jogi_researcher'], # type: ignore[index]
            verbose=self.is_verbose,
            temperature=0.1,
            max_retries=5,
            max_iter=5
        )

    @agent
    def jogi_grounding_verifier(self) -> Agent:
        return Agent(
            config=self.agents_config['jogi_grounding_verifier'],  # type: ignore[index]
            verbose=self.is_verbose,
            temperature=0.1,
            max_retries=5
        )

    @agent
    def jogi_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['jogi_advisor'], # type: ignore[index]
            verbose=self.is_verbose,
            temperature = 0.1,
            max_retries=5
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def jogi_strategiai_tervezes_feladat(self) -> Task:
        return Task(
            config=self.tasks_config['jogi_strategiai_tervezes_feladat'], # type: ignore[index]
        )

    @task
    def jogi_kutatasi_feladat(self) -> Task:
        return Task(
            config=self.tasks_config['jogi_kutatasi_feladat'],  # type: ignore[index]
        )

    @task
    def jogszabalyi_megalapozottsag_feladat(self) -> Task:
        return Task(
            config=self.tasks_config['jogszabalyi_megalapozottsag_feladat'], # type: ignore[index]
            output_file='report.md'
        )

    @task
    def jogi_tanacsadoi_feladat(self) -> Task:
        return Task(
            config=self.tasks_config['jogi_tanacsadoi_feladat'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the JogiAgent crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=self.is_verbose,
            memory=Memory(embedder=self.get_embedding_function)
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
