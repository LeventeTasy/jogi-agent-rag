import os
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase
from deepeval.test_case import LLMTestCaseParams
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
    SummarizationMetric,
    ToxicityMetric,
    BiasMetric,
    GEval
)
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")


def evaluate_multi_agent_system(input_text, actual_output, retrieval_context):
    MODEL_NAME = "gemini-flash-lite-latest"

    model = GeminiModel(
        model=MODEL_NAME,
        api_key=API_KEY,
        temperature=0
    )

    faithfulness = FaithfulnessMetric(threshold=0.5, model=model)
    answer_relevancy = AnswerRelevancyMetric(threshold=0.5, model=model)
    context_relevancy = ContextualRelevancyMetric(threshold=0.5, model=model)
    summarization = SummarizationMetric(threshold=0.5, model=model)
    toxicity = ToxicityMetric(threshold=0.5, model=model)
    bias = BiasMetric(threshold=0.5, model=model)

    coherence = GEval(
        name="Coherence",
        criteria="Determine how logically connected, flowy and coherent the actual output is.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.5,
        model=model
    )


    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_output,
        retrieval_context=retrieval_context
    )

    metrics = [
        faithfulness, answer_relevancy, context_relevancy,
        summarization, toxicity, bias, coherence
    ]

    for metric in metrics:
        metric.measure(test_case)

    results = {
        "Faithfulness": faithfulness.score,
        "Faithfulness_Reason": faithfulness.reason,
        "Answer_Relevancy": answer_relevancy.score,
        "Answer_Relevancy_Reason": answer_relevancy.reason,
        "Context_Relevancy": context_relevancy.score,
        "Context_Relevancy_Reason": context_relevancy.reason,
        "Summarization": summarization.score,
        "Summarization_Reason": summarization.reason,
        "Coherance": coherence.score,  # Spelled your way bestie! ✨
        "Coherance_Reason": coherence.reason,
        "Toxicity": toxicity.score,
        "Toxicity_Reason": toxicity.reason,
        "Bias": bias.score,
        "Bias_Reason": bias.reason
    }

    return results



if __name__ == "__main__":
    input_q = "A munkáltató felmondhat-e a munkaviszony kezdetétől számított hat hónapon belül, ha a felek korábban megállapodtak abban, hogy a munkaviszony felmondással nem szüntethető meg?"


    agent_output = """
    # JOGI SZAKVÉLEMÉNY: A munkáltató felmondhat-e a munkaviszony kezdetétől számított hat hónapon belül, ha a felek korábban megállapodtak abban, hogy a munkaviszony felmondással nem szüntethető meg?

### RÖVID VÁLASZ
Igen, a munkáltató felmondhat, mivel a felmondási jog kizárására vonatkozó megállapodás jogszabályba ütközik, és ezért érvénytelen.

### JOGI INDOKOLÁS
A 2012. évi I. törvény a munka törvénykönyvéről (a továbbiakban: Mt.) 65. § (1) bekezdése értelmében a munkáltató a határozatlan tartamú munkaviszonyt felmondással megszüntetheti. Ezen jogosultság alapvető munkajogi intézmény, amely a munkaviszony rugalmas megszüntetését biztosítja a törvényi keretek között.

A felek azon megállapodása, amely a munkaviszony felmondással történő megszüntetését a munkaviszony kezdetétől számított hat hónapon belül kizárja, ütközik az Mt. kógens rendelkezéseivel. Az Mt. 82. § (1) bekezdése kifejezetten rögzíti, hogy a munkaviszony megszüntetésére vonatkozó jogszabályi rendelkezések kógensek, azokat a felek megállapodása nem írhatja felül, kivéve, ha a törvény erre kifejezetten lehetőséget ad. Mivel az Mt. 87. § (1) bekezdése kimondja, hogy a munkaviszony megszüntetésének módjait a törvény határozza meg, és e szabályoktól érvényesen eltérni – ha a törvény eltérő rendelkezést nem tartalmaz – nem lehet, a felmondási jog korlátozása vagy kizárása érvénytelennek minősül.

A 2013. évi V. törvény a Polgári Törvénykönyvről (a továbbiakban: Ptk.) 6:96. §-a értelmében a törvényes rendelkezéssel ellentétes szerződés semmis. Mivel a felmondási jog kizárása a hatályos munkajogi rendelkezésekkel szemben áll, az ilyen tartalmú szerződéses kikötés semmissége folytán nem akadályozza a munkáltatót a törvényben biztosított felmondási jog gyakorlásában.

### JOGSZABÁLYI HIVATKOZÁSOK
* 2012. évi I. törvény a munka törvénykönyvéről: 43. § (1), 65. § (1), 82. § (1), 87. § (1) bekezdés.
* 2013. évi V. törvény a Polgári Törvénykönyvről: 6:96. §, 6:114. § (1) bekezdés.

### KOCKÁZATI TÉNYEZŐK ÉS KIVÉTELEK
A felmondási jog korlátozásának érvénytelensége a Ptk. 6:114. § (1) bekezdése alapján vizsgálható abból a szempontból, hogy a munkaszerződés egészét érinti-e a semmisség. Kockázatot jelenthet az a tény, hogy amennyiben a felek a felmondás tilalmát a szerződés lényeges elemévé tették (azaz e kikötés nélkül a munkaszerződést nem kötötték volna meg), az érvénytelen rész a teljes munkaszerződés érvénytelenségét vonhatja maga után. A munkáltatónak eljárásrendi kockázattal kell számolnia a felmondás indokolása kapcsán, mivel a jogszabályba ütköző kikötés érvénytelensége nem mentesíti a munkáltatót az Mt. 65. § (2)-(3) bekezdésében előírt indokolási kötelezettség alól."""

    retrieved_rag_chunks = [
        """65. §
(1) A munkaviszonyt mind a munkavállaló, mind a munkál-
tató felmondással megszüntetheti.    
(2) A felek megállapodása esetén – legfeljebb a munkaviszony kez-
detétől számított egy évig – a munkaviszony felmondással nem 
szüntethető meg.
41
(3) A munkáltató felmondással nem szüntetheti meg a munkavi-
szonyt  
a) a várandósság,
b) a szülési szabadság,
c) az apasági szabadság,
d) a szülői szabadság,
e) a gyermek gondozása céljából igénybe vett fizetés nélküli sza-
badság (128. §, 130. §),
f) a tényleges önkéntes tartalékos katonai szolgálatteljesítés,
g) a nő jogszabály szerinti, az emberi reprodukciós eljárással 
összefüggő kezelésének, de legfeljebb ennek megkezdésétől szá-
mított hat hónap, és
h) az 55. § (1) bekezdés l) pontja szerinti mentesülés
tartama alatt.
(4) A (3) bekezdés szerinti védelem alkalmazása szempontjából 
a felmondás közlésének, csoportos létszámcsökkentés esetén a 75. 
§ (1) bekezdés szerinti tájékoztatás közlésének időpontja az irány-
adó.  
(5) A munkavállaló a (3) bekezdés a) és g) pontjában meghatáro -
zott körülményre akkor hivatkozhat, ha erről a munkáltatót tájé -
koztatta. A felmondás közlését követő munkavállalói tájékoztatás -
tól számított tizenöt napon belül a munkáltató a felmondást írásban 
visszavonhatja.  
(6) A felmondás visszavonása esetén a 83. § (2)–(4) bekezdését 
kell alkalmazni.

44. §
(1) A kisgyermekkel otthon lévők szövetkezete közgyűlésén 
a vagyoni hozzájárulás mértékére tekintet nélkül minden tagnak 
egy szavazata van.
(2) A döntéshozatalra egyebekben az e §-ban nem szabályozott 
kérdésekben a Ptk. vonatkozó szabályai irányadóak.

39. §
A kisgyermekkel otthon lévők szövetkezetének nem lehet 
személyes közreműködést nem vállaló tagja.

193. §
(2) bekezdés c) pont], személyi szabadság megsértése [Btk.

43. §
(1) A kisgyermekkel otthon lévők szövetkezete által nyújtott 
szolgáltatásokért szolgáltatási díjat kell fizetni.
(2) A kisgyermekkel otthon lévők szövetkezete az éves nettó árbe-
vételének legalább 85%-át a tagok között személyes közreműködé-
sük arányában osztja fel.

11. §
(1) Egyszerűsített foglalkoztatás esetén a munkáltató köteles 
az illetékes elsőfokú állami adóhatóságnak a munkavégzés meg-
kezdése előtt bejelenteni a (2) bekezdés szerinti adatokat. A  mun-
káltató bejelentési kötelezettségét    
a) elektronikus azonosítását követő elektronikus kapcsolattartás 
útján, vagy
b) országos telefonos ügyfélszolgálaton keresztül telefonon
teljesíti.
(2) A munkáltató bejelentési kötelezettségét az (1) bekezdésben 
meghatározott módon, az egyszerűsített foglalkoztatás céljából 
létesített munkaviszonyra vonatkozó alábbi adatok közlésével tel -
jesíti:
a) a munkavállaló neve,
b) a munkáltató adószáma,
215
c) a munkavállaló adóazonosító jele és társadalombiztosítási azo-
nosító jele,
d) az egyszerűsített foglalkoztatás 1. § (1) bekezdés szerinti jel -
lege,
e) a munkaviszony napjainak száma.
(3) Ha a munkavállaló a szociális biztonsági rendszerek koordi-
nálásáról és annak végrehajtásáról szóló uniós rendeletek, vagy 
a Magyarország által kötött kétoldalú szociálpolitikai, szociális 
biztonsági egyezmény alapján másik tagállamban, illetve egyez -
ményben részes másik államban biztosított, és ezt a munkáltató 
előtt igazolta, az egyszerűsített foglalkoztatásra irányuló jogvi-
szony létesítésekor ezen körülményt az illetékes állami adóható -
ságnak a munkáltató az egyszerűsített foglalkoztatás bejelentésével 
egyidejűleg bejelenteni köteles.
(4) A  munkáltató az (1) bekezdésben meghatározott esetekben 
a tárgyhót követő hó 12-éig az egyszerűsítetten foglalkoztatott 
munkavállaló foglalkoztatásával járó közteher-fizetési kötelezett -
ségének tesz eleget. Bevallási kötelezettségét ezen időpontig elekt-
ronikusan teljesíti.
(5) Az a munkáltató, aki a 300 ezer forintot, vagy ezt megha -
ladó összegű adótartozást halmoz fel a 8. § (2) bekezdésében és/
vagy a 8. § (3) bekezdés a) pontjában szereplő adók tekintetében, 
további egyszerűsített foglalkoztatásra nem jogosult mindaddig, 
míg adótartozását ki nem egyenlíti.
(6) Az egyszerűsített foglalkoztatás (1) bekezdés b) pontja szerint 
történő bejelentése a jogszabályban meghatározott országos tele -
fonos ügyfélszolgálat által fenntartott ügyfélvonalon keresztül tör -
ténik, a bejelentő adóazonosító jelének megadásával. Az országos 
telefonos ügyfélszolgálat a bejelentést a jogszabályban meghatá -
rozott módon rögzíti, és a bejelentőt a bejelentés eredményéről 
egyidejűleg tájékoztatja. Az országos telefonos ügyfélszolgálat az 
adatokat haladéktalanul továbbítja az állami adóhatóság számára.
216
Az országos telefonos ügyfélszolgálat a bejelentett adatokat a beje-
lentést követő ötödik év december 31-éig őrzi meg, azt követően 
törlésre kerül. Az országos telefonos ügyfélszolgálat e törvényben 
meghatározott személyes adatokat, továbbá az adótitkot a feladat 
teljesítéséhez szükséges mértékben megismerheti és kezelheti.
(7) Az adóhatóság részére teljesített bejelentés esetleges visszavo-
nására és módosítására  
a) az egyszerűsített foglalkoztatás bejelentését követő két órán 
belül, vagy
b) ha a bejelentésben foglaltak szerint a foglalkoztatás a bejelen-
tés napját követő napon kezdődött, vagy ha a bejelentés egy nap-
nál hosszabb időtartamú munkaviszonyra vonatkozott, a módosítás 
bejelentés napján délelőtt 9 óráig
van lehetőség, ezt követően a munkáltató a közteher-fizetési köte-
lezettségének köteles eleget tenni. A  bejelentés módosítására az 
(1) bekezdésben foglaltak szerint kerülhet sor, függetlenül attól, 
hogy bejelentési kötelezettségének eredetileg a munkáltató melyik 
módon tett eleget.
(8) Az állami adóhatóság a munkáltató (1) bekezdés szerinti beje-
lentését visszautasítja, ha a munkaviszony napjainak száma az 1. § 
(4) bekezdésébe ütközik. A  foglalkoztató ebben az esetben a 8. § 
(4) bekezdése szerint köteles eljárni.  
(9) Az 1. § (4) bekezdés feltételeinek vizsgálata céljából az egy-
szerűsített foglalkoztatásra irányuló jogviszony létesítését megelő -
zően a foglalkoztató jogosult a természetes személy adóazonosító 
jelének, TAJ-számának és nevének megismerésére és kezelésére. 
Az 1. § (4) bekezdés szerinti feltétel vizsgálatához az állami adó- 
és vámhatóság elektronikus lekérdezési lehetőséget biztosít.

29. §
(1) Az érvénytelen megállapodás alapján létrejött jogvi-
szonyból származó jogokat és kötelezettségeket úgy kell tekin -
teni, mintha azok érvényes megállapodás alapján állnának fenn. Az 
érvénytelen megállapodás alapján létrejött jogviszonyt – ha e tör -
vény eltérően nem rendelkezik – a munkáltató köteles haladéktala-
nul, azonnali hatállyal megszüntetni, feltéve, hogy az érvénytelen -
ség okát a felek nem hárítják el.    
(2) A munkáltató köteles a munkavállalónak annyi időre járó távol-
léti díjat megfizetni, amennyi a munkáltató felmondása esetén 
járna, továbbá megfelelően alkalmazni kell a végkielégítés szabá-
lyait is, ha a munkaszerződés a munkáltató oldalán felmerült okból 
érvénytelen és azt az (1) bekezdés alapján meg kell szüntetni.
(3) Ha a megállapodás valamely része érvénytelen, helyette a mun-
kaviszonyra vonatkozó szabályt kell alkalmazni, kivéve, ha a felek 
az érvénytelen rész nélkül nem állapodtak volna meg.
(4) Az egyoldalú jognyilatkozat érvénytelensége esetén e jognyi-
latkozatból jogok és kötelezettségek nem származnak.
(5) A  munkaviszony megszüntetésére irányuló jognyilatkozat 
érvénytelensége esetén – a munkáltató saját jognyilatkozatának 
sikeres megtámadását kivéve – a 82–84. §-ban foglalt rendelkezé -
seket kell megfelelően alkalmazni.

149. §
(1) Havi bér esetén a távolléti díj 148. § (1) bekezdés a) pont
87
szerinti részének meghatározásakor a 136. § (3) bekezdésében fog-
laltakat kell alkalmazni.   
(2) A távolléti díj 148. § (1) bekezdés a) pont szerinti része a havi- 
vagy órabér és pótlékátalány távollét tartamára történő kifizetésé -
vel is teljesíthető és elszámolható.

125. §
A munkaviszony megszűnésekor, ha a munkáltató az ará-
nyos szabadságot nem adta ki, azt – az apasági szabadságot és 
a szülői szabadságot kivéve – meg kell váltani.
75
61. Betegszabadság

263. §
A munkáltató és az üzemi tanács közösen dönt a jóléti célú 
pénzeszközök felhasználása tekintetében.

101. §
(1) Vasárnapra rendes munkaidő  
a) a rendeltetése folytán e napon is működő munkáltatónál vagy 
munkakörben,
b) az idényjellegű,
c) a megszakítás nélküli,
d) a több műszakos tevékenység keretében,
e) a készenléti jellegű munkakörben,
f) a kizárólag szombaton és vasárnap részmunkaidőben,
g) társadalmi közszükségletet kielégítő, vagy külföldre történő 
szolgáltatás nyújtásához – a szolgáltatás jellegéből eredően – e 
napon szükséges munkavégzés esetén,
h) külföldön történő munkavégzés során, valamint
i) a kereskedelemről szóló törvény hatálya alá tartozó, kereske-
delmi tevékenységet, a kereskedelmet kiszolgáló szolgáltató, vala-
mint kereskedelmi jellegű turisztikai szolgáltatási tevékenységet 
folytató munkáltatónál
foglalkoztatott munkavállaló számára osztható be.
(2) Az (1) bekezdés a) pont tekintetében a 102. § (3) bekezdése 
megfelelően irányadó.
63
(3)

9. §
(1) A  munkavállaló és a munkáltató személyiségi jogai -
nak védelmére, ha e törvény eltérően nem rendelkezik, a Polgári 
Törvénykönyvről szóló 2013. évi V . törvény (a továbbiakban: Ptk.) 
2:42–54. §-át kell alkalmazni azzal, hogy a Ptk. 2:52. § (2) és (3) 
bekezdése, valamint 2:53. §-a alkalmazásakor e törvény kártérítési 
felelősségre vonatkozó szabályai az irányadók.    
(2) A munkavállaló személyiségi joga akkor korlátozható, ha a kor-
látozás a munkaviszony rendeltetésével közvetlenül összefüggő 
okból feltétlenül szükséges és a cél elérésével arányos. A személyi-
ségi jog korlátozásának módjáról, feltételeiről és várható tartamáról, 
továbbá szükségességét és arányosságát alátámasztó körülményekről
5
a munkavállalót előzetesen írásban tájékoztatni kell.
(3) A munkavállaló a személyiségi jogáról általános jelleggel előre 
nem mondhat le. A munkavállaló személyiségi jogáról rendelkező 
jognyilatkozatot érvényesen csak írásban tehet.
5/A. Adatkezelés

8. §
(2) bekezdését és 10. § (2) bekezdését a 2025. február 1-jét 
követően keletkezett, e törvény szerinti foglalkoztatási jogviszo-
nyok esetében kell alkalmazni.
(2) A Magyarország 2025. évi központi költségvetésének megala -
pozásáról szóló 2024. évi LXXIV . törvénnyel megállapított 1. § (4) 
bekezdését 2025. július 1-jétől kell alkalmazni úgy, hogy a 2025. 
évben a foglalkoztatás időtartamának számításakor annak 120 nap-
tári napos korlátját 2025. július 1-jétől kell figyelembe venni.
221
(3) A Magyarország 2025. évi központi költségvetésének megala -
pozásáról szóló 2024. évi LXXIV . törvénnyel megállapított 8. § (2) 
bekezdése szerint megállapított közterhek mértékét és a nyugellá-
tás 10. § (2) bekezdése szerint meghatározott alapját az állami adó-
hatóság 2025. január 20-áig honlapján és a Magyar Közlönyben 
közzéteszi.

244. §
(1) A  választás eredményét a választási bizottság állapítja 
meg.  
(2) A választási bizottság jegyzőkönyvet készít. Ennek tartalmaz -
nia kell különösen
a) a választásra jogosultak számát,
b) a szavazáson részt vevők számát,
c) a leadott érvényes és érvénytelen szavazatok számát,
d) az egyes jelöltekre leadott szavazatok számát,
e) a megválasztott üzemi tanácstagok és póttagok nevét,
f) a választással összefüggő esetleges vitás ügyet és az ezzel kap-
csolatos döntést.
(3) A választási jegyzőkönyvet a választási bizottság haladéktala -
nul közzéteszi.
(4) Az üzemi tanács megbízatása a választási jegyzőkönyv közzé-
tételét követő munkanapon kezdődik.

232. §
A  munkáltató, az üzemi tanács, a szakszervezet köteles
127
egymást írásban tájékoztatni a képviseletére jogosult, valamint 
a tisztségviselő személyéről."""
    ]

    eredmenyek = evaluate_multi_agent_system(input_q,agent_output,retrieved_rag_chunks)

    import json

    print(json.dumps(eredmenyek, indent=4, ensure_ascii=False))