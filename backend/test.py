import os
import sys
from contextlib import suppress

# Ensure we can import the app package when run from project root or container
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app.database import SessionLocal  # type: ignore
from app import models  # type: ignore


def seed_cours():
    db = SessionLocal()
    try:
        # Ensure tables exist
        models.Base.metadata.create_all(bind=db.get_bind())

        # Fetch up to two existing cours (ordered by id)
        existing = db.query(models.Cours).order_by(models.Cours.id).limit(2).all()

        if not existing:
            # create 3 modules
            for i in range(1, 4):
                m = models.Module(
                    titre=f"Module {i}",
                    description=f"Description du module {i}",
                )
                db.add(m)

            # Create two cours with modified titre/description/contenu
            created = []
            for i in range(1, 3):
                if (i == 1):
                    c = models.Cours(
                        titre=f"Les sources d'informations",
                        description=f"Comprendre et évaluer les sources d'information",
                        contenu=f"Description des sources d'informations.",
                    )
                if (i == 2):
                        c = models.Cours(
                            titre=f"OUI",
                            description=f"OUIOUI",
                            contenu=f"OUIOUIOUI",
                        )
                db.add(c)
                created.append(c)
            db.commit()
            for c in created:
                db.refresh(c)
            cours_to_process = created
            print("Created 2 cours with modified content")
        else:
            # Update the first two existing cours' fields
            cours_to_process = []
            for idx, c in enumerate(existing):
                if (idx == 0):
                    c.titre = f"Les sources d'informations"
                    c.description = f"Comprendre et évaluer les sources d'information"
                    c.contenu = f"Description des sources d'informations."
                    c.id_module = 1
                    cours_to_process.append(c)
                if (idx == 1):
                    c.titre = f"OUI"
                    c.description = f"OUIOUI"
                    c.contenu = f"OUIOUIOUI"
                    c.id_module = 2
                    cours_to_process.append(c)
            db.commit()
            # refresh objects
            for c in cours_to_process:
                db.refresh(c)
            print(f"Updated {len(cours_to_process)} existing cours")

        cours1 = 0
        cours2 = 0

        # For each cours ensure there are 3 pages and at least one QCM
        for c in cours_to_process:
            # reload fresh instance to access relationships
            fresh = db.query(models.Cours).filter(models.Cours.id == c.id).one()

            # Ensure 3 pages
            current_pages = list(fresh.pages or [])
            for p_index in range(len(current_pages) + 1, 4):
                if(cours1 == 0):
                    if(p_index == 1):
                        page = models.Page(
                            description=f"Qu'est-ce qu'une source d'information ? {p_index}",
                            content=(
                                "Une source d'information est l'origine des données ou faits rapportés par les médias. "
                                "Elle peut être un témoin direct, un document officiel, un expert ou un média reconnu. "
                                "La fiabilité d'une source dépend de son indépendance, de sa transparence et de sa cohérence "
                                "avec d'autres sources crédibles."
                            ),
                            medias="journaliste_interview.jpg",
                            est_vue=0,
                            id_cours=fresh.id,
                        )
                    if(p_index == 2):
                        page = models.Page(
                            description=f"Types de sources d'information {p_index}",
                            content=("Les sources d'information peuvent être classées selon leur nature. "
                                "Les sources primaires sont des témoignages directs et des documents originaux comme des rapports et des discours. "
                                "Les sources secondaires sont des analyses et commentaires basés sur des sources primaires. "
                                "Les sources tertiaires sont des compilations de sources secondaires, comme les encyclopédies. "

                                "Comprendre la nature d'une source permet d'évaluer son degré de fiabilité."
                            ),
                            medias="source_primaire_secondaire.png",
                            est_vue=0,
                            id_cours=fresh.id,
                        )
                    if(p_index == 3):
                        page = models.Page(
                            description=f"Comment vérifier la fiabilité d'une source ? {p_index}",
                            content=(
                                "Vérifier la crédibilité d'une source nécessite une approche critique : Il est important d'identifier l'auteur et de s'assurer de son expertise. "

                                "L'objectif de la source doit être analysé pour distinguer l'information de l'influence. Une information fiable peut être vérifiée par d'autres sources crédibles. "
                                "L'ancienneté de la source joue aussi un rôle, une source récente pouvant être pertinente mais moins éprouvée."
                            ),
                            medias="fake_news_verification.png",
                            est_vue=0,
                            id_cours=fresh.id,
                        )
                    cours1 = 1
            if(cours2 == 0):
                if(p_index == 1):
                    page = models.Page(
                        description=f"Qu'est-ce qu'une source d'information ? {p_index}",
                        content=(
                            "Une source d'information est l'origine des données ou faits rapportés par les médias. "
                            "Elle peut être un témoin direct, un document officiel, un expert ou un média reconnu. "
                            "La fiabilité d'une source dépend de son indépendance, de sa transparence et de sa cohérence "
                            "avec d'autres sources crédibles."
                        ),
                        medias="journaliste_interview.jpg",
                        est_vue=0,
                        id_cours=fresh.id,
                    )
                if(p_index == 2):
                    page = models.Page(
                        description=f"Types de sources d'information {p_index}",
                        content=("Les sources d'information peuvent être classées selon leur nature. "
                            "Les sources primaires sont des témoignages directs et des documents originaux comme des rapports et des discours. "
                            "Les sources secondaires sont des analyses et commentaires basés sur des sources primaires. "
                            "Les sources tertiaires sont des compilations de sources secondaires, comme les encyclopédies. "

                            "Comprendre la nature d'une source permet d'évaluer son degré de fiabilité."
                        ),
                        medias="source_primaire_secondaire.png",
                        est_vue=0,
                        id_cours=fresh.id,
                    )
                if(p_index == 3):
                    page = models.Page(
                        description=f"Comment vérifier la fiabilité d'une source ? {p_index}",
                        content=(
                            "Vérifier la crédibilité d'une source nécessite une approche critique : Il est important d'identifier l'auteur et de s'assurer de son expertise. "

                            "L'objectif de la source doit être analysé pour distinguer l'information de l'influence. Une information fiable peut être vérifiée par d'autres sources crédibles. "
                            "L'ancienneté de la source joue aussi un rôle, une source récente pouvant être pertinente mais moins éprouvée."
                        ),
                        medias="fake_news_verification.png",
                        est_vue=0,
                        id_cours=fresh.id,
                    )
                    cours2 = 1
                db.add(page)

            if (cours1 == 0):
                if not (fresh.qcms and len(fresh.qcms) > 0):
                    q = models.QCM(
                        question=f"Quel est le principal indicateur de la fiabilité d'une source d'information ?",
                        rep1="Sa popularité sur les réseaux sociaux",
                        rep2="La vérifiabilité des informations par d'autres sources fiables",
                        rep3="Le nombre de commentaires sous l'article",
                        rep4="Le design du site web",
                        soluce=2,
                        id_cours=fresh.id,
                    )
                    db.add(q)

                    q2 = models.QCM(
                        question=f"Quelle est la meilleure manière de vérifier une information trouvée en ligne ?",
                        rep1="La partager immédiatement avec ses amis",
                        rep2="Consulter plusieurs sources fiables et vérifier la cohérence de l'information",
                        rep3="Faire confiance à la première source trouvée",
                        rep4="Vérifier si l'information est amusante avant de la croire",
                        soluce=2,
                        id_cours=fresh.id,
                    )
                    db.add(q2)

                    q3 = models.QCM(
                        question=f"Quel est un signe révélateur d'une fausse information ?",
                        rep1="Elle provient d'un média reconnu et sérieux",
                        rep2="Elle utilise un ton sensationnaliste et manque de sources vérifiables",
                        rep3="Elle cite plusieurs experts et références",
                        rep4="Elle est reprise par plusieurs médias de confiance",
                        soluce=2,
                        id_cours=fresh.id,
                    )
                    db.add(q3)

                    cours1 = 1

            # if(cours2 == 0):
            #     if not (fresh.qcms and len(fresh.qcms) > 0):
            #         q = models.TextATrous(
            #             texte=f"Le principal indicateur de la fiabilité d'une source d'information est la __________ des informations par d'autres sources fiables.",
            #             reponse1="Popularité sur les réseaux sociaux",
            #             reponse2="Elle utilise un ton sensationnaliste et manque de sources vérifiables",
            #             reponse3="Elle cite plusieurs experts et références",
            #             reponse4="Elle est reprise par plusieurs médias de confiance",
            #             soluce=2,
            #             id_cours=fresh.id,
            #         )

        db.commit()
        print("Ensured 3 pages and 1 QCM for each cours processed")
    finally:
        with suppress(Exception):
            db.close()


if __name__ == "__main__":
    seed_cours()
