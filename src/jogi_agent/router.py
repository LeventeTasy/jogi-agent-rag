import time
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from crewai import LLM
from dotenv import load_dotenv
from jogi_agent.flow import JogiFlow
import os

from jogi_agent.utils import initialize_firebase


class RouterFlow(Flow):

    def __init__(self, /, testing=False, **data: any):
        super().__init__(**data)
        self.start_time = time.perf_counter()

    @start()
    def init_flow(self):
        load_dotenv()
        self.state["model"] = str(os.getenv("MODEL"))
        self.state["question"] = self.state["inputs"]["topic"]

        if "history" not in self.state or not self.state["history"]:
            self.state["history"] = self.state.get("inputs", {}).get("history", "")


        self.state["chunks"] = ""
        self.state["verifier_counter"] = ""

        if self.state["inputs"]["chatID"] == "":
            self.state["inputs"]["chatID"] = f"C_{uuid.uuid4()}".upper()
        self.state["question_id"] = f'{self.state["inputs"]["chatID"]}-{self.state["inputs"]["questionNumber"]}'



    @router(init_flow)
    def main(self):

        SYSTEM_PROMPT = f'''
        Te egy szigorú, bináris osztályozó modell (Router) vagy egy magyar jogi AI asszisztens rendszer kapujában.
        A feladatod a beérkező felhasználói üzenet szándékának (intent) vizsgálata és besorolása a korábbi beszélgetési kontextus figyelembevételével.
        
        Beszélgetési előzmény:
        "{self.state["history"]}"
        
        SZABÁLYOK:
        1. Két lehetséges kategória létezik:
           - "LEGAL": Ha a felhasználó kérdése vagy üzenete közvetlenül vagy közvetve magyar jogi szabályozással, törvényekkel (pl. Munka Törvénykönyve, Ptk., Btk., GDPR, Adójog, fogyasztóvédelem), hatósági eljárásokkal, szerződésekkel, munkaviszonnyal vagy jogi vitákkal kapcsolatos.
           - "NOT_LEGAL": Ha az üzenet:
             * Csupán üdvözlés, köszönés, elköszönés (pl. "Szia", "Jó napot", "Helló").
             * Megköszönés vagy udvariassági formula (pl. "Köszönöm", "Szuper, köszi", "Hálás vagyok").
             * Nem jogi témájú általános kérdés (pl. receptek, időjárás, matematika, programozás, popkultúra).
             * Értelmetlen szöveg, karakterhalmaz, tesztelés (pl. "asdasd", "123").
             * Általános csevegés vagy a modell képességeire vonatkozó kérdés (pl. "Ki vagy te?", "Hogy vagy?").
        
        2. BIZTONSÁGI / DÖNTÉSI IRÁNYELV:
           - Ha az üzenet köznapi megfogalmazású, de egyértelműen jogi helyzetre utal (pl. "Kirúgott a főnököm, mit csináljak?", "Átvert az eladó az interneten", "Nem kaptam fizetést"), akkor a besorolás: "LEGAL".
           - Ha bizonytalan vagy, de nincs benne konkrét jogi vagy jogszabályi elem, a válasz: "NOT_LEGAL".
        
        3. KIMENETI FORMÁTUM (SZIGORÚ):
           Kizárólag a két kulcsszó egyikét válaszold vissza, bármiféle írásjel, magyarázat, bevezető vagy szóköz nélkül, nagy betűvel írva:
           LEGAL
           vagy
           NOT_LEGAL
        '''

        llm = LLM(model=self.state["model"])
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": self.state["question"]},
        ]
        response = llm.call(messages)

        if "not_legal" in response.lower():
            return "NOT_LEGAL"
        elif "legal" in response.lower():
            return "LEGAL"
        else:
            return "HIBA"

    @listen("LEGAL")
    def call_main_flow(self):
        flow = JogiFlow()
        flow.state["inputs"] = self.state["inputs"]
        flow.state["history"] = self.state["history"]

        resp = flow.kickoff()

        self.state["history"] = flow.get_history()
        self.state["question_id"] = flow.get_question_id()
        self.state["chunks"] = flow.get_chunks()
        self.state["verifier_counter"] = flow.get_verifier_counter()
        self.state["chatID"] = flow.get_chat_id()

        return resp

    @listen("NOT_LEGAL")
    def call_etc(self):
        self.state["question_id"] = f"Q_{uuid.uuid4()}".upper()

        llm = LLM(model=self.state["model"])

        SYSTEM_PROMPT = """
        Te a "Magyar Jogi AI Asszisztens" rendszer információs és kapuőr komponense vagy.
        Kizárólag akkor lépsz működésbe, amikor a felhasználó bemenete NEM minősül konkrét, megválaszolható magyar jogi kérdésnek (pl. üdvözlés, elköszönés, megköszönés, általános csevegés vagy nem jogi témájú megkeresés).
        
        ALAPVETŐ SZABÁLYOK ÉS TULAJDONSÁGOK:
        
        1. IDENTITÁS ÉS JOGI NYILATKOZAT (DISCLAIMER):
           - Te egy mesterséges intelligencia alapú jogi tájékoztató rendszer vagy.
           - FONTOS KORLÁTOZÁS: Te kizárólag általános jogi tájékoztatást és támpontokat tudsz nyújtani. NEM minősülsz hivatalos ügyvédi képviseletnek vagy jogi tanácsadónak.
           - Mindig hangsúlyozd szükség esetén, hogy konkrét, éles jogi ügyekben, peres eljárásokban elengedhetetlen egy hivatalos jogi szakember (ügyvéd, jogtanácsos) felkeresése.
        
        2. SZIGORÚ TÉMAHŰSÉG (NO FUN / NO CHATBOT ROLEPLAY):
           - Ne bocsátkozz általános csevegésbe, ne mesélj vicceket, ne írj verseket, és ne válaszolj nem jogi témájú kérdésekre (pl. receptek, időjárás, programozás, popkultúra, matematika).
           - Ha a felhasználó nem jogi kérdést tesz fel: Tömören, udvariasan, de határozottan közöld, hogy a rendszer kifejezetten és kizárólag magyar jogi kérdések megválaszolására és törvényszövegek elemzésére lett kifejlesztve, így az adott nem jogi kérdésre nem tudsz választ adni.
        
        3. VÁLASZADÁSI MÓDOK HELYZETEK SZERINT:
           - Üdvözlés / Köszönés (pl. "Szia", "Jó napot"): Üdvözöld a felhasználót röviden és professzionálisan, majd kérdezd meg, milyen magyar jogi kérdésben vagy helyzetben segíthetsz neki.
           - Megköszönés / Pozitív visszajelzés (pl. "Köszönöm", "Köszi a segítséget"): Fogadd udvariasan (pl. "Szívesen! Ha bármilyen további jogi kérdése merülne fel, készséggel állok rendelkezésére.").
           - Nem jogi témájú kérdés (pl. "Hogy kell palacsintát sütni?", "Ki nyerte a meccset?"): Jelezd, hogy ez a kérdés nem kapcsolódik a magyar joghoz, így nem áll módodban megválaszolni, és kérd meg, hogy tegyen fel jogi jellegű kérdést.
           - Értelmetlen / Teszt jellegű szöveg (pl. "asdasd"): Udvariasan jelezd, hogy nem sikerült értelmezni az üzenetet, és kérd meg a jogi kérdés megfogalmazására.
        
        4. HANGNEM ÉS STÍLUS:
           - Professzionális, udvarias, tárgyilagos, tömör és hivatalos magyar nyelvezet.
           - Kerüld a túlzottan hosszú körmondatokat, maradj lényegretörő (maximum 2-3 mondatban válaszolj).
        """

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": self.state["question"]},
        ]
        self.state["final_answer"] = llm.call(messages)
        self.save_log_fb()

        return self.state["final_answer"]

    @listen("HIBA")
    def error_handling(self):
        return "Hiba történt a router ágenssel!"

    def get_history(self):
        return self.state["history"]

    def get_question_id(self):
        return self.state["question_id"]

    def get_chunks(self):
        return self.state["chunks"]

    def get_verifier_counter(self):
        return self.state["verifier_counter"]

    def get_chat_id(self):
        return self.state["inputs"]["chatID"]

    def save_log(self):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        PATH = BASE_DIR / "logs" / "log.xlsx"

        log = pd.read_excel(PATH)

        log.loc[len(log)] = {
            "QuestionID": self.state["question_id"],
            "UserID": "U_1",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Question": self.state["inputs"]["topic"],
            "Answer": self.state["final_answer"],
            "Runtime": time.perf_counter() - self.start_time,
        }

        log.to_excel(PATH, index=False)

    def save_log_fb(self):
        db = initialize_firebase()

        db.collection("nl_questions").add(
            {
                "QuestionID": self.state["question_id"],
                "UserID": "U_1",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Question": self.state["inputs"]["topic"],
                "Answer": self.state["final_answer"],
                "Runtime": time.perf_counter() - self.start_time,
            }
        )