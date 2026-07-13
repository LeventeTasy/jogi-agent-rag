from crewai import Crew, Process
from crewai.flow import human_feedback
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from dotenv import load_dotenv
from .crew import JogiAgent
from jogi_agent.utils import get_config

load_dotenv()

class JogiFlow(Flow):

    @start()
    def init_flow(self):
        config = get_config()
        self.state["is_verbose"] = config["is_verbose"]
        self.state["deep_analysis"] = config["is_deep_analysis_enabled"]

        if "inputs" not in self.state:
            self.state["inputs"] = {}

    @router(init_flow)
    def route_config(self):
        if self.state["deep_analysis"]:
            return "run_deep_analysis"
        else:
            return "skip_deep_analysis"

    @human_feedback(message="Kérjük pontosítsa a leírt szituációt (Enter = kihagyás):")
    @listen("run_deep_analysis")
    def deep_analysis(self):
        agent_instance = JogiAgent()

        mini_crew = Crew(
            agents=[agent_instance.jogi_strategist()],
            tasks=[agent_instance.inditasi_feladat(), agent_instance.deep_analysis_feladat()],
            verbose=self.state["is_verbose"]
        )

        analysis_result = mini_crew.kickoff(inputs=self.state["inputs"])

        return analysis_result.raw

    @listen(deep_analysis)
    def process_feedback(self, result):

        if result.feedback:  # Ha adott meg plusz infót
            # print(f"Bekerülő új infó: {result.feedback}")
            jelenlegi_details = self.state["inputs"].get("details", "")

            if jelenlegi_details:
                self.state["inputs"]["details"] = jelenlegi_details + f"\nTovábbi pontosítás: {result.feedback}"
            else:
                self.state["inputs"]["details"] = f"Felhasználó kiegészítése: {result.feedback}"
        # else:
        # print("A felhasználó kihagyta a válaszadást (Enter).")


    @listen(or_(process_feedback, "skip_deep_analysis"))
    def run_main_crew(self, *args):
        #print("Starting flow")
        #print(f"Flow State ID: {self.state['id']}")

        agent_instance = JogiAgent()
        agent_instance.is_deep_analysis = False
        flow_inputs = self.state["inputs"]
        crew_result = agent_instance.crew().kickoff(inputs=flow_inputs)


        # Kinyerjük a tisztított RAG találatokat
        self.state["rag_chunks"] = crew_result.tasks_output[3].raw

        # Kinyerjük a tanácsadó véleményét
        self.state["final_answer"] = crew_result.tasks_output[5].raw

        # Kinyerjük az ellenőrző ágens véleményét
        self.state["verifier_feedback"] = crew_result.tasks_output[6].raw


    @router(run_main_crew)
    def check_answer(self):

        if "HIBA ÉSZLELVE!" in self.state["verifier_feedback"]:
            return "javitas"
        elif "SIKER, ELLENŐZÉS BEFEJEZVE" in self.state["verifier_feedback"]:
            return "complete" # Ha a verifier jóváhagyja
        else:
            return "undecidable" # Ha a verifier agent rosszul címkézett

    @listen("javitas")
    def correction(self):
        print("Jogi Segéd újrafuttatása, korrekció folyamatban...")

        jogi_seged = JogiAgent()
        advisor_agent = jogi_seged.jogi_advisor()
        advisor_task = jogi_seged.jogi_tanacsadoi_feladat()

        # FRISSÍTJÜK A PROMPT-OT DINAMIKUSAN! 🪄
        # Ahelyett, hogy a YAML-ből olvasná, átadjuk neki a RAG kontextust ÉS a hibaüzenetet is!
        advisor_task.description += \
            f"""
            Javítsd ki a korábbi jogi válaszodat!

            A nyers törvényi kontextus (RAG chunks): 
            {self.state['rag_chunks']}

            Az ellenőrző ágens az alábbi hibákat találta a válaszodban, ezeket KÖTELEZŐ javítanod:
            {self.state['verifier_feedback']}

            Kérlek, generálj egy új, javított szakvéleményt! 
            FONTOS: Válaszodban csak a RAG chunkokra hagyadkozz!
            """

        # Megjegyzés: Memory-ra későbbiekben lehet szükség lesz
        mini_crew = Crew(
            agents=[advisor_agent],
            tasks=[advisor_task],
            process=Process.sequential,
            verbose=self.state["is_verbose"]
        )

        self.state["final_answer"] = mini_crew.kickoff().raw

    @listen("undecidable")
    def warning_undecidable(self):
        print("Hiba: Verifier agent - Rossz címkézés")
        return "Hiba: Verifier agent - Rossz címkézés\n" + self.state["final_answer"]

    @listen(correction)
    def finish_flow(self):
        return self.state["final_answer"]

