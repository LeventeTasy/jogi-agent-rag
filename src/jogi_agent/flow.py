from crewai import Crew, Process
from crewai.flow.flow import Flow, listen, start, router
from dotenv import load_dotenv
from .crew import JogiAgent
from jogi_agent.utils import get_config

load_dotenv()

class JogiFlow(Flow):

    @start()
    def start_flow(self):
        #print("Starting flow")
        #print(f"Flow State ID: {self.state['id']}")

        agent_instance = JogiAgent()
        flow_inputs = self.state.get("inputs", {})
        crew_result = agent_instance.crew().kickoff(inputs=flow_inputs)


        # Kinyerjük a tisztított RAG találatokat
        self.state["rag_chunks"] = crew_result.tasks_output[1].raw

        # Kinyerjük a tanácsadó véleményét
        self.state["final_answer"] = crew_result.tasks_output[3].raw

        # Kinyerjük az ellenőrző ágens véleményét
        self.state["verifier_feedback"] = crew_result.tasks_output[4].raw


    @router(start_flow)
    def check_answer(self):

        if "HIBA ÉSZLELVE!" in self.state["verifier_feedback"]:
            return "javítás"
        elif "SIKER, ELLENŐZÉS BEFEJEZVE" in self.state["verifier_feedback"]:
            return "complete" # Ha a verifier jóváhagyja
        else:
            return "undecidable" # Ha a verifier agent rosszul címkézett

    @listen("javitas")
    def correction(self):
        print("Jogi Segéd újrafuttatása, korrekció folyamatban...")

        config = get_config()
        is_verbose = config["is_verbose"]

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
            verbose=is_verbose
        )

        self.state["final_answer"] = mini_crew.kickoff().raw
        return "complete"

    @listen("undecidable")
    def warning_undecidable(self):
        print("Hiba: Verifier agent - Rossz címkézés")
        return "Hiba: Verifier agent - Rossz címkézés\n" + self.state["final_answer"]

    @listen("complete")
    def finish_flow(self):
        return self.state["final_answer"]

    # Ha egy magánszemély visszavonja a hozzájárulását egy webshopban, és kéri az elfeledtetéshez való jog alapján az összes vásárlási adatának és számlájának azonnali törlését, a webshop köteles-e ennek eleget tenni a GDPR szerint?
