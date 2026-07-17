import json
from crewai import Crew, Process
from crewai.flow import human_feedback
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from dotenv import load_dotenv
from .crew import JogiAgent
from jogi_agent.utils import get_config
import re

load_dotenv()

class JogiFlow(Flow):

    def __init__(self, /, testing=False, **data: any):
        super().__init__(**data)
        self.testing = testing

    @start()
    def init_flow(self):
        config = get_config()
        self.state["is_verbose"] = config["is_verbose"]
        self.state["deep_analysis"] = config["is_deep_analysis_enabled"]

        self.state["correction_retries"] = 0
        self.state["max_retries"] = 2

        self.state["rag_chunks"] = ""
        self.state["cleaned_rag_chunks"] = ""
        self.state["final_answer"] = ""
        self.state["verifier_feedback"] = ""

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
        rag_task = agent_instance.jogi_kutatasi_feladat()
        megalapozottsag_task = agent_instance.jogszabalyi_megalapozottsag_feladat()
        advisor_task = agent_instance.jogi_tanacsadoi_feladat()
        verifier_task = agent_instance.jogszabalyi_ellenőzési_feladat()


        agent_instance.is_deep_analysis = False
        flow_inputs = self.state["inputs"]
        crew_result = agent_instance.crew().kickoff(inputs=flow_inputs)

        self.state["rag_chunks"] = rag_task.output.raw
        self.state["cleaned_rag_chunks"] = megalapozottsag_task.output.raw
        self.state["final_answer"] = advisor_task.output.raw
        self.state["verifier_feedback"] = verifier_task.output.raw

    def get_chunks(self):
        flow_output_string = self.state["cleaned_rag_chunks"]

        if not flow_output_string:
            print("Hiba: A cleaned_rag_chunks üres!")
            return []

        try:
            # Biztonsági mentés: Ha a terminálos Rich/Box keret karakterek (│) benne maradtak, kisöpörjük őket
            if "│" in flow_output_string:
                flow_output_string = flow_output_string.replace("│", "")

            # Regexszel kivágjuk a [ ] tömböt
            match = re.search(r'\[.*\]', flow_output_string, re.DOTALL)

            if not match:
                print("Hiba: Nem találtam érvényes JSON tömböt [ ] a szövegben!")
                return []

            cleaned_json = match.group(0).strip()
            crew_sources = json.loads(cleaned_json)

            extracted_chunks_list = []

            # Végigmegyünk a kapott elemeken
            for item in crew_sources:
                if not isinstance(item, dict):
                    continue

                # 1. ESZET: Ha a régi, beágyazott struktúrát kaptuk (van 'results' kulcs)
                if "results" in item and isinstance(item["results"], list):
                    for result in item["results"]:
                        quote = result.get("quote", "").strip()
                        source = result.get("source", "").strip()
                        article = result.get("article", "").strip()
                        raw_text = result.get("raw_text", "").strip()

                        final_text = raw_text if raw_text else quote
                        if final_text:
                            extracted_chunks_list.append(f"[{source} - {article}]: {final_text}")

                # 2. ESET: Ha a mostani, lapos struktúrát kaptuk (maga az elem a találat)
                else:
                    quote = item.get("quote", "").strip()
                    source = item.get("source", "").strip()
                    article = item.get("article", "").strip()
                    raw_text = item.get("raw_text", "").strip()

                    # Ha van raw_text, az a legjobb, ha nincs, jó lesz a quote is!
                    final_text = raw_text if raw_text else quote
                    if final_text:
                        extracted_chunks_list.append(f"[{source} - {article}]: {final_text}")

            return extracted_chunks_list

        except Exception as e:
            print(f"Nem sikerült JSON-ná alakítani: {e}")
            return []

        except Exception as e:
            print(f"Nem sikerült JSON-ná alakítani: {e}")
            print(f"A problémás string: {flow_output_string}")
            return []

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

        correction_agent = jogi_seged.jogi_fact_checker()
        correction_task = jogi_seged.jogszabalyi_ellenőzési_feladat()

        # Frissitjuk az advisor promptot dinamikusan
        advisor_task.description = f"""
        KÖTELEZŐ JAVÍTÁSI FELADAT! A korábbi jogi válaszod elbukott az ellenőrzésen.
        
        Itt van a KORÁBBI (HIBÁS) VÁLASZOD, amit ki kell javítanod:
        {self.state['final_answer']}
        
        AZ ELLENŐRZŐ ÁGENS JELENTÉSE (Ezeket a hibákat kell kijavítanod a fenti szövegben):
        {self.state['verifier_feedback']}
        
        A HITELES RAG FORRÁSSZÖVEGEK (Csak és kizárólag ezekre támaszkodhatsz):
        {self.state['rag_chunks']}
        
        FONTOS: Ne találj ki új törvényeket, ne csonkíts idézeteket! 
        Módosítsd a korábbi válaszodat a jelentés alapján, és generáld le a tökéletesen javított, végleges verziót!
        """

        if "RAG FORRÁS:" not in correction_task.description:
            correction_task.description += f""" 
                RAG FORRÁS:
                {self.state['rag_chunks']}
                                            """

        if self.state["correction_retries"] < self.state["max_retries"]:

            self.state["correction_retries"] += 1
            mini_crew = Crew(
                agents=[advisor_agent, correction_agent],
                tasks=[advisor_task, correction_task],
                process=Process.sequential,
                verbose=self.state["is_verbose"]
            )


            while self.state["correction_retries"] < self.state["max_retries"]:

                mini_crew_result = mini_crew.kickoff()

                self.state["final_answer"] = mini_crew_result.tasks_output[0].raw
                self.state["verifier_feedback"] = mini_crew_result.tasks_output[1].raw

                if "SIKER, ELLENŐRZÉS BEFEJEZVE" in self.state["verifier_feedback"]:
                    print("A korrekció sikeres.")
                    return

                self.state["correction_retries"] += 1

        else:
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

    @listen(or_(correction, "complete"))
    def finish_flow(self):
        if self.testing:
            return self.state["final_answer"] + f"\n RAG CHUNKS: {self.state['rag_chunks']}"

        else:
            return self.state["final_answer"]

