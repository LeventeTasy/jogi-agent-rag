import os
import pandas as pd


munka_torvenykonyv = [
    # KÖNNYŰ KÉRDÉSEK (15 db)
    "Köteles-e a munkáltató írásba foglalni a munkaszerződést, és mi a következménye, ha ez elmarad?",
    "Hány nap szabadság jár alapbérként egy 22 éves munkavállalónak Magyarországon?",
    "Megszüntethető-e a munkaviszony azonnali hatállyal a próbaidő alatt indokolás nélkül?",
    "Köteles-e a munkavállaló indokolni a felmondását, ha határozatlan idejű munkaviszonyt szüntet meg?",
    "Hány nap rendkívüli szabadság jár a munkavállalónak a gyermeke születése esetén (apasági szabadság)?",
    "Milyen határidővel kell a munkáltatónak kifizetnie a munkabért a tárgyhónapot követően?",
    "Követelhet-e a munkáltató kártérítést a munkavállalótól, ha az gondatlanul kárt okoz a cég eszközében?",
    "Hány óra a törvényes napi munkaidő (teljes munkaidő) főszabály szerint?",
    "Kiadhatja-e a munkáltató a szabadságot a munkavállaló kérése ellenére is?",
    "Milyen életkortól lestesíthető munkaviszony törvényesen Magyarországon?",
    "Kötelezhető-e a várandós munkavállaló éjszakai munka végzésére?",
    "Mi a különbség a munkaviszony és a megbízási jogviszony között a munkavégzés önállósága szempontjából?",
    "Jár-e végkielégítés a munkavállalónak, ha ő maga mond fel rendes felmondással?",
    "Hogyan kell elszámolni a túlórát (rendkívüli munkaidőt) a munkavállaló felé?",
    "Visszautasíthatja-e a munkavállaló a munkaszerződéstől eltérő munkahelyen történő átmeneti foglalkoztatást?",
    # NEHÉZ KÉRDÉSEK (5 db)
    "Milyen feltételek teljesülése esetén hivatkozhat a munkáltató 'állásidőre', és mentesülhet-e a távolléti díj megfizetése alól elháríthatatlan külső ok (vis maior) miatt?",
    "Egy munkavállaló a betegszabadsága alatt szóban jelenti be a felmondását a felettesének, aki azt tudomásul veszi. Joghatásos-e ez a felmondás, és mikor kezdődik a felmondási idő?",
    "A munkáltató jogutód nélküli megszűnése esetén hogyan alakul a munkavállaló végkielégítésre és felmondási időre járó távolléti díjra való jogosultsága?",
    "Áthelyezhető-e egyoldalúan a munkavállaló egy másik cégcsoporton belüli munkáltatóhoz anélkül, hogy új munkaszerződést kötnének?",
    "Hogyan minősül a munkaviszony megszüntetése, ha a munkáltató csoportos létszámcsökkentést hajt végre, de nem tartja be a törvényben előírt 30 napos előzetes tájékoztatási kötelezettséget?"
]

gdpr = [
    # KÖNNYŰ KÉRDÉSEK (15 db)
    "Milyen jogalapok alapján kezelhet személyes adatot egy adatkezelő a GDPR szerint?",
    "Visszavonhatja-e az érintett a hozzájárulását az adatkezeléshez, és ha igen, milyen következményekkel?",
    "Mit jelent a 'felejtéshez való jog' (törléshez való jog) a GDPR értelmében?",
    "Milyen határidőn belül köteles az adatkezelő bejelenteni az adatvédelmi incidenst a hatóságnak (NAIH)?",
    "Kinek az adatát tekintjük 'személyes adatnak' a GDPR definíciója szerint?",
    "Kötelező-e minden cégnek adatvédelmi tisztviselőt (DPO) kineveznie?",
    "Mit takar az 'adathordozhatósághoz való jog' lényege?",
    "Kezelhető-e jogszerűen egy munkavállaló telefonszáma a munkáltató által hozzájárulás nélkül is?",
    "Milyen feltételekkel kezelhetők kiskorúak személyes adatai az információs társadalommal összefüggő szolgáltatásoknál?",
    "Mit jelent az 'adattakarékosság' elve a gyakorlatban?",
    "Kötelező-e az adatvédelmi tájékoztatót (Privacy Policy) könnyen érthető nyelvezettel megfogalmazni?",
    "Büntethet-e a hatóság egyéni vállalkozót is GDPR megsértése miatt, vagy csak nagyvállalatokat?",
    "Mi minősül adatvédelmi incidensnek a GDPR szabályai szerint?",
    "Szükséges-e az érintett hozzájárulása, ha az adatkezelés jogszabályi kötelezettség teljesítéséhez kell?",
    "Mit jelent az 'előzetes tájékoztatás' elve az adatgyűjtés megkezdése előtt?",
    # NEHÉZ KÉRDÉSEK (5 db)
    "Alapozhatja-e a munkáltató a munkavállalók e-mailes fiókjainak ellenőrzését kizárólag a 'jogos érdek' (legitimate interest) jogalapjára, és ha igen, milyen kötelező vizsgálatot kell előtte elvégeznie?",
    "Egy cég harmadik országba (pl. USA) szeretne ügyféladatokat továbbítani. Milyen jogi garanciák (pl. SCC, Adequacy Decision) szükségesek ahhoz, hogy ez ne ütközzön a GDPR-ba?",
    "Hogyan érvényesül az 'adatkezelés korlátozásához való jog' (restriciton of processing) abban az esetben, ha az érintett vitatja a személyes adatok pontosságát?",
    "Milyen esetekben kötelező az Adatvédelmi Hatásvizsgálat (DPIA) lefolytatása egy új szoftver bevezetése előtt, és mi történik, ha a vizsgálat magas kockázatot mutat ki?",
    "Közös adatkezelésnek minősül-e, ha két önálló cég közös marketingkampányt indít, és hogyan kell szabályozniuk egymás közötti felelősség megosztását az érintettek felé?"
]

ptk = [
    # KÖNNYŰ KÉRDÉSEK (15 db)
    "Mikor jön létre érvényesen egy szerződés a Ptk. szerint?",
    "Mit jelent a cselekvőképesség, és kiből válhat korlátozottan cselekvőképes személy?",
    "Mi a különbség a tulajdonjog és a birtokjog között?",
    "Hány év a felelősség és a követelések elévülési ideje főszabály szerint a Ptk.-ban?",
    "Köthető-e érvényes adásvételi szerződés szóban egy nagy értékű ingóságra (pl. laptop)?",
    "Milyen felelősséggel tartozik az a személy, aki másnak jogellenesen kárt okoz?",
    "Mit jelent az előszerződés intézménye és mi a jogi kötelező ereje?",
    "Kik minősülnek törvényes örökösnek a Ptk. végrendelet hiányában alkalmazandó szabályai szerint?",
    "Mi a következménye annak, ha a szerződő felek egyike késedelembe esik a teljesítéssel?",
    "Milyen jogi személy típusokat határoz meg a Ptk. a gazdasági társaságok körében?",
    "Hogyan lehet érvényesen felmondani egy határozatlan időre kötött bérleti szerződést?",
    "Mit jelent a 'jóhiszeműség és tisztesség' alapelve a polgári jogi jogviszonyokban?",
    "Kérhet-e sérelemdíjat az a személy, akinek megsértették a személyiségi jogait?",
    "Mi a zálogjog lényege, és hogyan nyújt biztonságot a hitelezőnek?",
    "Mikor minősül egy szerződéses kikötés tisztességtelennek a fogyasztói szerződésekben?",
    # NEHÉZ KÉRDÉSEK (5 db)
    "Milyen feltételek együttes fennállása esetén hivatkozhat egy fél sikeresen a 'szerződésszegéssel okozott kártérítési felelősség alóli mentesülésre' (vis maior a Ptk. 6:142. § alapján)?",
    "Hogyan alakul a felelősség megoszlása, ha az eladó hibásan teljesít (kellékszavatosság), de a vevő elmulasztja a hiba felfedezése utáni haladéktalan közlési kötelezettségét?",
    "Mit jelent az utólagos lehetetlenülés a szerződés teljesítése során, és hogyan oszlik meg a kárveszély a felek között, ha egyik fél sem felelős a lehetetlenülésért?",
    "Milyen feltételekkel támadható meg sikeresen egy szerződés 'feltűnő értékaránytalanság' (laesio enormis) jogcímén, and mikor zárja ki a törvény a megtámadhatóságot?",
    "A képviseleti jog nélkül eljáró álképviselő (falsus procurator) által kötött szerződés milyen feltételek teljesülése esetén válik érvényessé, és ki viseli a kárt, ha a képviselt nem hagyja jóvá a szerződést?"
]

szja = [
    # KÖNNYŰ KÉRDÉSEK (15 db)
    "Hány százalék a személyi jövedelemadó (SZJA) általános kulcsa jelenleg Magyarországon?",
    "Ki minősül belföldi illetőségű magánszemélynek az SZJA törvény alkalmazásában?",
    "Milyen határidőig kell benyújtani az éves SZJA bevallást a magánszemélyeknek?",
    "Milyen feltételekkel vehető igénybe a 25 év alatti fiatalok SZJA-kedvezménye?",
    "Adómentesnek minősül-e a munkavállalónak fizetett kiküldetési rendelvény alapján adott utazási költségtérítés?",
    "Mi az a családi adókedvezmény, és hány gyermek után vehető igénybe?",
    "Terheli-e SZJA fizetési kötelezettség a saját ingatlan értékesítéséből származó jövedelmet, ha az eladás 5 évnél régebben vásárolt ingatlanra vonatkozik?",
    "Mi minősül bérjövedelemnek és hogyan adózik az SZJA szerint?",
    "Hogyan adózik a magánszemélynek kifizetett osztalékjövedelem?",
    "Mi az az adóalap-kedvezmény, és hogyan csökkenti a ténylegesen fizetendő adót?",
    "Ki köteles az SZJA adóelőleget megállapítani és levonni a munkabérből?",
    "Igénybe vehető-e SZJA kedvezmény tartós betegség vagy súlyos fogyatékosság esetén?",
    "Milyen adózási szabályok vonatkoznak a reprezentációs költségekre és az üzleti ajándékokra?",
    "Mit jelent az 'önadózás' elve az SZJA rendszerében?",
    "Hogyan kell adózni az önkéntes kölcsönös biztosítópénztári befizetések után járó adó-visszatérítéssel?",
    # NEHÉZ KÉRDÉSEK (5 db)
    "Hogyan kell meghatározni az SZJA-alapot és a fizetendő adót, ha egy magánszemély külföldi devizában kapja az egyéb forrásból származó jövedelmét, és milyen árfolyamot kell alkalmazni az átszámításkor?",
    "Milyen speciális adózási szabályok és sávos kedvezmények vonatkoznak a 30 év alatti anyák kedvezményére, ha a jogosultsági évben szerzett jövedelme meghaladja a törvényi értékhatárt?",
    "Hogyan adózik a munkavállaló által kapott opciós jog vagy ingyenesen/kedvezményesen juttatott értékpapír megszerzése (dolgozói részvényjuttatási program), és mikor keletkezik az adókötelezettség?",
    "Milyen feltételek mellett minősül egy magánszemély ingatlan-bérbeadási tevékenysége üzletszerűnek, és hogyan választhat az 10%-os költséghányad és a tételes költségelszámolás között?",
    "Hogyan elszámolni és adóztatni a magánszemély által külföldről kapott jogdíjat vagy licencdíjat, ha a forrásország és Magyarország között van kettős adóztatás elkerüléséről szóló egyezmény?"
]

osszetett = [
    "Egy munkavállaló céges laptopján az IT osztály jogosulatlanul átvizsgálja a privát mappákat, ahol bizonyítékot találnak arra, hogy a munkavállaló egyéni vállalkozóként adózatlan bevételeket szerez az SZJA kijátszásával. A munkáltató azonnali hatállyal felmond neki az Mt. alapján. Megtámadhatja-e a munkavállaló a felmondást a GDPR megsértésére hivatkozva a munkaügyi perben, és hogyan érinti az SZJA-elmaradás a jogvitát?",
    "Egy cég a munkavállalók hozzájárulása nélkül gyűjti azok biometrikus adatait (ujjlenyomat) a beléptetőrendszerhez. Az egyik dolgozó megtagadja az adást, ezért a munkáltató állásidőre helyezi és nem fizet neki bért. Megvalósul-e itt a GDPR megsértése, jogszerű-e az Mt. szerinti állásidő alkalmazása, és ha a dolgozó emiatt kártérítést követel, az polgári jogi (Ptk.) vagy munkajogi felelősség alá tartozik?",
    "A munkáltató egyoldalúan, a munkavállaló tudta nélkül kamerát szerel fel az irodában. A felvételek alapján kiderül, hogy a dolgozó szándékosan összetörte a cég egyik nagy értékű gépét. A munkáltató azonnal felmond (Mt.), követeli a gép értékét (Ptk.), és a videót bizonyítékként benyújtja. Felhasználható-e a GDPR-ellenes felvétel a Ptk. szerinti kártérítési perben és az Mt. szerinti munkaügyi perben?",
    "Egy magánszemély bérbe adja az ingatlanát egy cégnek. A bérleti szerződést (Ptk.) a bérlő cég egyik munkatársa írja alá álképviselőként. A cég nem fizeti ki a bérleti díjat, és nem vonja le az SZJA-előleget sem. Ha a bérbeadó pert indít, érvényes-e a szerződés a Ptk. szerint, ki felel az adóhiányért az SZJA törvény alapján, és hogyan érinti ez a cég belső munkajogi felelősségét?",
    "Egy munkavállaló felmond a munkahelyén, és kéri a személyes adatainak törlését (GDPR 'felejtéshez való jog'). A munkáltató azonban megtagadja a törlést, arra hivatkozva, hogy az Szja törvény és a számviteli szabályok miatt a bérszámfejtési adatokat és a munkaszerződést (Mt.) még évekig meg kell őriznie. Kinek van igaza a GDPR és az Mt./Szja törvények ütközésében?",
    "Egy cég az SZJA-mentes cafeteria juttatásokat (SZJA tv.) csak azon munkavállalóknak biztosítja, akik hozzájárulnak ahhoz, hogy a cég az egészségügyi adataikat (GDPR különleges adat) marketing célokra harmadik félnek továbbítsa. Megszegi-e a cég az Mt. egyenlő bánásmód elvét, jogszerű-e a GDPR szerinti hozzájárulás ebben a kiszolgáltatott helyzetben, és milyen adójogi következményei vannak a juttatások visszavonásának?",
    "Egy ügyvezető a Ptk. szerinti megbízási jogviszonyban látja el a feladatait, de a cég úgy dönt, hogy az Szja kedvezőbb adózása miatt színlelt munkaszerződéssel (Mt.) foglalkoztatja tovább. A NAV egy ellenőrzés során feltárja a színlelt szerződést. Milyen adójogi (SZJA) szankciókra számíthatnak, hogyan minősül át a jogviszony a Ptk. és az Mt. szerint, és ki felel az elmaradt adók befizetéséért?",
    "Egy munkavállaló gondatlanságból súlyos adatvédelmi incidenst okoz (GDPR), amiért a hatóság (NAIH) 10 millió forintos bírságot szab ki a cégre. A munkáltató a teljes összeget le akarja vonni a munkavállaló munkabéréből kártérítésként (Mt. és Ptk. deliktuális kárfelelősség). Milyen korlátok közé esik a munkavállaló anyagi felelőssége, és követelhető-e tőle a hatósági bírság megtérítése?",
    "Egy külsős egyéni vállalkozó megbízási szerződéssel (Ptk.) dolgozik egy cégnek, de a cég úgy kezeli az adatait, mintha belső munkavállaló lenne (GDPR). A NAV vizsgálata szerint a jogviszony valójában munkaviszonynak (Mt.) minősül. Hogyan változik meg a vállalkozó SZJA adózása a jogviszony átminősítése után, és milyen adatvédelmi felelősség terheli a céget a korábbi jogszerűtlen adatkezelésért?",
    "Egy cég eladja az egyik üzletágát egy másik vállalatnak (munkáltatói jogutódlás az Mt. szerint). Az átvevő cég átveszi a munkavállalók adatait is (GDPR), de az egyik dolgozó nem akar az új cégnél dolgozni, ezért azonnali hatályú felmondást nyújt be és követeli a végkielégítését (Mt. és Ptk.). Jogszerű-e az adattovábbítás hozzájárulás nélkül az üzletág-átadáskor, és jár-e a dolgozónak a végkielégítés?",
    "Egy munkavállaló táppénz alatt (Mt. felmondási tilalom és betegszabadság) egyéni vállalkozóként (Ptk. szerződéses jogviszony) számlázott be más cégeknek, és ebből SZJA-köteles jövedelme származott. A munkáltató ezt megtudja, és azonnali hatállyal felmond neki az Mt. jóhiszeműség elvének megsértése miatt. Jogszerű-e a felmondás, és hogyan érinti a betegszabadság alatti adóköteles munkavégzés a TB és SZJA kötelezettségeket?",
    "Egy cég a volt munkavállalója céges e-mail fiókját a kilépése után hónapokig aktívan tartja és olvassa az oda érkező leveleket (GDPR megsértése). Az e-mailek között találnak egy szerződéstervezetet, amiből kiderül, hogy a volt dolgozó megszegte a Ptk. szerinti versenytilalmi megállapodását. Követelheti-e a cég a Ptk. szerinti kötbért a GDPR-ellenesen szerzett bizonyítékok alapján az Mt. hatáskörében folyó perben?",
    "Egy magánszemély a Ptk. szerinti vállalkozási szerződés keretében szoftvert fejleszt egy cégnek. A szerződés szerint a szerzői jogok a céget illetik meg. A fejlesztő nem vallja be az ebből kapott összeget az SZJA bevallásában. Később a cég a szoftverben lévő felhasználói adatokat (GDPR) harmadik félnek értékesíti. Megtilthatja-e a fejlesztő a szoftver használatát a Ptk. alapján az adóelkerülés és a GDPR megsértése miatt?",
    "A munkáltató kötelező jelleggel GPS nyomkövetőt szerel a munkavállaló saját tulajdonú gépjárművébe, amit munkavégzésre is használ (Mt. és GDPR). A hétvégi, magáncélú használat adatait is rögzítik, és ez alapján felmondanak a dolgozónak, mert túl gyorsan hajtott (Ptk. szerződésszegés és Mt.). Jogszerű-e az így szerzett adatok alapján történő felmondás, és hogyan alakul a gépjármű magánhasználatának SZJA-vonzata?",
    "Egy munkavállaló a cég belső whistleblower (visszaélés-bejelentő) rendszerén keresztül jelentést tesz arról, hogy a pénzügyi igazgató SZJA-csalást követ el. A bejelentő adatait (GDPR) a cég gondatlanságból kiadja a pénzügyi igazgatónak, aki emiatt zaklatni kezdi és ellehetetleníti a dolgozót (Mt. és Ptk. személyiségi jogi jogsértés). Milyen kártérítést és sérelemdíjat követelhet a dolgozó a Ptk. és az Mt. alapján?",
    "Egy cég a koronavírus-járvány alatt kötelezővé tette a tesztelést, és a pozitív eredményű dolgozókat állásidőre helyezte, de az SZJA-mentes egészségügyi hozzájárulást (SZJA tv.) megvonta tőlük. A dolgozók pert indítanak az Mt. szerinti egyenlő bánásmód megsértése, a GDPR szerinti különleges adatok jogellenes kezelése és a Ptk. szerinti elmaradt juttatások megfizetése miatt. Hogyan döntsön a bíróság?",
    "Egy külföldi kiküldetésben lévő munkavállaló (Mt.) a kiküldetési rendelvényen szereplő összegeket nem a munkájára, hanem magáncélra költi (Ptk. jogalap nélküli gazdagodás). A munkáltató ezt a cég bankkártya-adatainak (GDPR) ellenőrzésével bizonyítja be, és levonja az összeget a bérből, miközben az SZJA bevallásban ezt reprezentációs juttatásként tünteti fel. Jogszerű-e az ellenőrzés, a levonás, és mi a NAV álláspontja az SZJA-ról?",
    "Egy cég a munkavállalók teljesítményértékelését egy külsős AI szoftverre bízza, amely teljesen automatizált döntéssel (GDPR 22. cikk) kiválasztja a legrosszabbul teljesítő 5%-ot a csoportos létszámcsökkentéshez (Mt.). A kiválasztott dolgozók a felmondás érvénytelenségét kérik a Ptk. jóhiszeműség elve és a GDPR megsértése miatt. Megállja-e a helyét az automatizált AI döntésen alapuló felmondás a bíróságon?",
    "Egy magánszemély a Ptk. szerinti ingyenes használati (haszonkölcsön) szerződéssel átadja autóját a cégének. A cég az autót a munkavállalóknak adja magánhasználatra (Mt.), de nem fizeti meg utána a cégautóadót és az SZJA-t. Az egyik dolgozó az autóval balesetet okoz, és a biztosító a GDPR-ra hivatkozva nem adja ki a tulajdonosnak a baleseti adatokat. Ki felel a kárért a Ptk. és az Mt. szerint, és ki az adóhiányért?",
    "Egy cég a HR adatbázisát (GDPR) egy olyan felhőben tárolja, amelyet feltörnek, és a munkavállalók bér- és SZJA-adatai nyilvánosságra kerülnek. Több dolgozó emiatt súlyos mentális stresszre hivatkozva sérelemdíjat követel (Ptk. és Mt. munkáltatói felelősség). Mentesülhet-e a munkáltató a felelősség alól, ha bizonyítja, hogy a felhőszolgáltató hibázott, and hogyan érinti ez a munkavállalók és a cég közötti jogviszonyt?"
]


columns = [
    "Törvény", "Típus", "Kérdés", "Q_chunk", "A_chunk",
    "Válasz", "Groundedness", "GroundednessReason", "ContextRelevance", "AnswerRelevance"
]

data_to_append = []


torveny_konfiguraciok = [
    (munka_torvenykonyv, "Munka Törvénykönyve (Mt.)"),
    (gdpr, "GDPR rendelet"),
    (ptk, "Polgári Törvénykönyv (Ptk.)"),
    (szja, "SZJA törvény")
]

for lista, torveny_nev in torveny_konfiguraciok:
    for index, kerdes in enumerate(lista):

        tipus = "könnyű" if index < 15 else "nehéz"
        data_to_append.append([
            torveny_nev,
            tipus,
            kerdes,
            "Kézi generálás",
            None, None, None, None, None, None
        ])


for kerdes in osszetett:
    data_to_append.append([
        "Kombinált",
        "összetett",
        kerdes,
        "Kézi generálás",
        None, None, None, None, None, None
    ])


uj_df = pd.DataFrame(data_to_append, columns=columns)


file_path = 'generated_test_questions.xlsx'

if os.path.exists(file_path):
    print(f"Meglévő fájl észlelve: {file_path}. Hozzáfűzés folyamatban...")
    regi_df = pd.read_excel(file_path)

    vegso_df = pd.concat([regi_df, uj_df], ignore_index=True)
else:
    print(f"Új fájl létrehozása folyamatban: {file_path}...")
    vegso_df = uj_df


vegso_df.to_excel(file_path, index=False)
print("Mind a 100 kérdés a megfelelő metaadatokkal elmentve!")