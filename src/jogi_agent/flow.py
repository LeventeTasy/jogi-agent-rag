import json
import time
from crewai import Crew, Process
from crewai.flow import human_feedback
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from dotenv import load_dotenv
from pathlib import Path
from .crew import JogiAgent
from jogi_agent.utils import get_config, initialize_firebase
import re
import uuid
import pandas as pd
from datetime import datetime


load_dotenv()

class JogiFlow(Flow):

    def __init__(self, /, testing=False, **data: any):
        super().__init__(**data)
        self.start_time = time.perf_counter()
        self.testing = testing

    @start()
    def init_flow(self):
        config = get_config()
        self.state["is_verbose"] = config["is_verbose"]
        self.state["deep_analysis"] = config["is_deep_analysis_enabled"]

        self.state["correction_retries"] = 0
        self.state["verifier_counter"] = 0
        self.state["max_retries"] = 2

        self.state["total_tokens"] = 0
        self.state["prompt_tokens"] = 0
        self.state["completion_tokens"] = 0
        self.state["successful_requests"] = 0
        self.state["question_id"] = f"Q_{uuid.uuid4()}".upper()

        self.state["agent1_output"] = ""            # 1. agens
        self.state["rag_chunks"] = ""               # 2. agens
        self.state["cleaned_rag_chunks"] = ""       # 3. agens
        self.state["final_answer"] = ""  # 4/5. agens
        self.state["verifier_feedback"] = ""        # 5. agens

        if "inputs" not in self.state:
            self.state["inputs"] = {}

        if "history" not in self.state:
            self.state["history"] = []

    def run_metrics(self, result):
        metrics = result.token_usage

        self.state["total_tokens"] += metrics.total_tokens
        self.state["prompt_tokens"] += metrics.prompt_tokens
        self.state["completion_tokens"] += metrics.completion_tokens
        self.state["successful_requests"] += metrics.successful_requests

    def get_question_id(self):
        return self.state["question_id"]

    def get_history(self):
        return self.state["history"]

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

        self.run_metrics(analysis_result)

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
        tervezo_feladat = agent_instance.jogi_strategiai_tervezes_feladat()
        rag_task = agent_instance.jogi_kutatasi_feladat()
        megalapozottsag_task = agent_instance.jogszabalyi_megalapozottsag_feladat()
        advisor_task = agent_instance.jogi_tanacsadoi_feladat()
        verifier_task = agent_instance.jogszabalyi_ellenőzési_feladat()


        agent_instance.is_deep_analysis = False
        flow_inputs = self.state["inputs"]
        crew_result = agent_instance.crew().kickoff(inputs=flow_inputs)
        self.run_metrics(crew_result)

        self.state["agent1_output"] = tervezo_feladat.output.raw
        self.state["rag_chunks"] = rag_task.output.raw
        self.state["cleaned_rag_chunks"] = megalapozottsag_task.output.raw
        self.state["final_answer"] = advisor_task.output.raw
        self.state["verifier_feedback"] = verifier_task.output.raw
        self.state["verifier_counter"] += 1


    def get_chunks(self):
        flow_output_string = self.state.get("cleaned_rag_chunks") or self.state.get("rag_chunks")
        if not flow_output_string:
            print("Hiba: A RAG chunks és a cleaned_rag_chunks is üres!")
            return []

        if "│" in flow_output_string:
            flow_output_string = flow_output_string.replace("│", "")

        clean_str = re.sub(r'```(?:json)?', '', flow_output_string)
        clean_str = re.sub(r'```', '', clean_str).strip()
        try:
            match = re.search(r'\[\s*\{.*\}\s*\]', clean_str, re.DOTALL)
            json_str = match.group(0).strip() if match else clean_str
            crew_sources = json.loads(json_str)
            extracted_chunks_list = []
            for item in crew_sources:
                if not isinstance(item, dict):
                    continue
                results_to_process = item.get("results", [item]) if isinstance(item.get("results"), list) else [item]
                for res in results_to_process:
                    if not isinstance(res, dict):
                        continue
                    quote = res.get("quote", "").strip()
                    raw_text = res.get("raw_text", "").strip()
                    text_alt = res.get("text", "").strip() or res.get("content", "").strip()

                    source = res.get("source", "").strip() or res.get("law", "").strip() or "RAG"
                    article = res.get("article", "").strip() or res.get("page", "").strip()
                    final_text = raw_text or quote or text_alt
                    if final_text:
                        header = f"[{source} - {article}]" if article else f"[{source}]"
                        extracted_chunks_list.append(f"{header}: {final_text}")
            if extracted_chunks_list:
                return extracted_chunks_list
        except Exception as e:
            print(f"JSON feldolgozási figyelmeztetés: {e}")

        raw_fallback = self.state.get("rag_chunks", "")
        if raw_fallback:
            clean_raw = re.sub(r'```(?:json)?', '', raw_fallback)
            clean_raw = re.sub(r'```', '', clean_raw).strip()

            fallback_lines = [
                line.strip() for line in clean_raw.split("\n")
                if line.strip() and not line.strip().startswith("{") and not line.strip().startswith("}")
            ]
            if fallback_lines:
                return ["\n".join(fallback_lines)]
        return []

    def get_verifier_counter(self):
        return self.state.get("verifier_counter")

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
                self.run_metrics(mini_crew_result)

                self.state["final_answer"] = mini_crew_result.tasks_output[0].raw
                self.state["verifier_feedback"] = mini_crew_result.tasks_output[1].raw
                self.state["verifier_counter"] += 1

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

            self.run_metrics(self.state["final_answer"])

    @listen("undecidable")
    def warning_undecidable(self):
        print("Hiba: Verifier agent - Rossz címkézés")
        return "Hiba: Verifier agent - Rossz címkézés\n" + self.state["final_answer"]

    def save_log(self):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        PATH = BASE_DIR / "logs" / "log.xlsx"

        log = pd.read_excel(PATH)

        log.loc[len(log)] = {
            "QuestionID": self.state["question_id"],
            "UserID": "U_1",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Question": self.state["inputs"]["topic"],
            "Chunks": self.get_chunks(),
            "Answer": self.state["final_answer"],
            "Runtime": time.perf_counter() - self.start_time,
            "Total_Tokens": self.state["total_tokens"],
            "Prompt_Tokens": self.state["prompt_tokens"],
            "Completion_Tokens": self.state["completion_tokens"],
            "Successful_Requests": self.state["successful_requests"],
            "Agent1_Output": self.state["agent1_output"],
            "Agent2_Output": self.state["rag_chunks"],
            "Agent3_Output": self.state["cleaned_rag_chunks"],
            "Agent5_Output": self.state["verifier_feedback"],
            "Verifier_Agent_Runs": self.state["verifier_counter"]
        }

        log.to_excel(PATH, index=False)

    def save_log_fb(self):
        db = initialize_firebase()

        db.collection("questions").add(
            {
                "QuestionID": self.state["question_id"],
                "UserID": "U_1",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Question": self.state["inputs"]["topic"],
                "Chunks": self.get_chunks(),
                "Answer": self.state["final_answer"],
                "Runtime": time.perf_counter() - self.start_time,
                "Total_Tokens": self.state["total_tokens"],
                "Prompt_Tokens": self.state["prompt_tokens"],
                "Completion_Tokens": self.state["completion_tokens"],
                "Successful_Requests": self.state["successful_requests"],
                "Agent1_Output": self.state["agent1_output"],
                "Agent2_Output": self.state["rag_chunks"],
                "Agent3_Output": self.state["cleaned_rag_chunks"],
                "Agent5_Output": self.state["verifier_feedback"],
                "Verifier_Agent_Runs": self.state["verifier_counter"]
            }
        )

    @listen(or_(correction, "complete"))
    def finish_flow(self):
        if self.state["inputs"]["details"] == "":
            self.state["history"].append({"role": "Felhasználó", "content": self.state["inputs"]["topic"]})
        else:
            self.state["history"].append({"role": "Felhasználó", "content": self.state["inputs"]["topic"] + f"\n###Felhasználó kiegészítése: {self.state['inputs']['details']}"})
        self.state["history"].append({"role": "Asszisztens", "content": self.state["final_answer"]})

        try:
            self.save_log_fb()
            self.save_log()
        except FileNotFoundError:
            print("Hiba: Log nem lett mentve!")
            pass

        if self.testing:
            return self.state["final_answer"] + f"\nVerifier futttatva: {self.state['verifier_counter']}" + f"\n RAG CHUNKS: {self.state['rag_chunks']}"

        else:
            return self.state["final_answer"]

