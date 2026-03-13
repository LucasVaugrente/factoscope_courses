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

        # ── CLEAN SLATE ──────────────────────────────────────────────────────────
        print("Suppression des données existantes…")
        db.query(models.QCM).delete()
        db.query(models.Page).delete()
        db.query(models.Cours).delete()
        db.query(models.Module).delete()
        db.commit()
        print("Tables vidées.")

        # ── MODULES ──────────────────────────────────────────────────────────────
        modules = []
        for i in range(1, 4):
            m = models.Module(
                titre=f"Module {i}",
                description=f"Description du module {i}",
            )
            db.add(m)
            modules.append(m)
        db.commit()
        for m in modules:
            db.refresh(m)
        print(f"{len(modules)} modules créés.")

        # ── COURS 1 : Les sources d'informations ─────────────────────────────────
        cours1 = models.Cours(
            titre="Les sources d'informations",
            description="Comprendre et évaluer les sources d'information",
            contenu="Description des sources d'informations.",
            id_module=modules[0].id,
        )
        db.add(cours1)
        db.commit()
        db.refresh(cours1)

        pages_cours1 = [
            models.Page(
                description="Qu'est-ce qu'une source d'information ?",
                content=(
                    "Une source d'information est l'origine des données ou faits rapportés par les médias. "
                    "Elle peut être un témoin direct, un document officiel, un expert ou un média reconnu. "
                    "La fiabilité d'une source dépend de son indépendance, de sa transparence et de sa cohérence "
                    "avec d'autres sources crédibles."
                ),
                medias="journaliste_interview.jpg",
                est_vue=0,
                id_cours=cours1.id,
            ),
            models.Page(
                description="Types de sources d'information",
                content=(
                    "Les sources d'information peuvent être classées selon leur nature. "
                    "Les sources primaires sont des témoignages directs et des documents originaux comme des rapports et des discours. "
                    "Les sources secondaires sont des analyses et commentaires basés sur des sources primaires. "
                    "Les sources tertiaires sont des compilations de sources secondaires, comme les encyclopédies. "
                    "Comprendre la nature d'une source permet d'évaluer son degré de fiabilité."
                ),
                medias="source_primaire_secondaire.png",
                est_vue=0,
                id_cours=cours1.id,
            ),
            models.Page(
                description="Comment vérifier la fiabilité d'une source ?",
                content=(
                    "Vérifier la crédibilité d'une source nécessite une approche critique : "
                    "Il est important d'identifier l'auteur et de s'assurer de son expertise. "
                    "L'objectif de la source doit être analysé pour distinguer l'information de l'influence. "
                    "Une information fiable peut être vérifiée par d'autres sources crédibles. "
                    "L'ancienneté de la source joue aussi un rôle, une source récente pouvant être pertinente mais moins éprouvée."
                ),
                medias="fake_news_verification.png",
                est_vue=0,
                id_cours=cours1.id,
            ),
        ]
        for p in pages_cours1:
            db.add(p)

        qcms_cours1 = [
            models.QCM(
                question="Quel est le principal indicateur de la fiabilité d'une source d'information ?",
                rep1="Sa popularité sur les réseaux sociaux",
                rep2="La vérifiabilité des informations par d'autres sources fiables",
                rep3="Le nombre de commentaires sous l'article",
                rep4="Le design du site web",
                soluce=2,
                id_cours=cours1.id,
            ),
            models.QCM(
                question="Quelle est la meilleure manière de vérifier une information trouvée en ligne ?",
                rep1="La partager immédiatement avec ses amis",
                rep2="Consulter plusieurs sources fiables et vérifier la cohérence de l'information",
                rep3="Faire confiance à la première source trouvée",
                rep4="Vérifier si l'information est amusante avant de la croire",
                soluce=2,
                id_cours=cours1.id,
            ),
            models.QCM(
                question="Quel est un signe révélateur d'une fausse information ?",
                rep1="Elle provient d'un média reconnu et sérieux",
                rep2="Elle utilise un ton sensationnaliste et manque de sources vérifiables",
                rep3="Elle cite plusieurs experts et références",
                rep4="Elle est reprise par plusieurs médias de confiance",
                soluce=2,
                id_cours=cours1.id,
            ),
        ]
        for q in qcms_cours1:
            db.add(q)

        db.commit()
        print(f"Cours 1 créé : {cours1.titre} — {len(pages_cours1)} pages, {len(qcms_cours1)} QCM")

        # ── COURS 2 : OUI ─────────────────────────────────────────────────────────
        cours2 = models.Cours(
            titre="OUI",
            description="OUIOUI",
            contenu="OUIOUIOUI",
            id_module=modules[0].id,
        )
        db.add(cours2)
        db.commit()
        db.refresh(cours2)

        pages_cours2 = [
            models.Page(
                description="Description 1",
                content=(
                    "La brève : Un texte court (5 à 10 lignes) qui donne une information essentielle sans commentaire. "
                    "L'article de presse : Développe un sujet avec des détails et des explications. "
                    "Il suit généralement la règle des 5W (Who, What, When, Where, Why)."
                ),
                medias="genre_d_information.jpg",
                est_vue=0,
                id_cours=cours2.id,
            ),
            models.Page(
                description="Description 2",
                content=(
                    "La brève : Un texte court (5 à 10 lignes) qui donne une information essentielle sans commentaire. "
                    "L'article de presse : Développe un sujet avec des détails et des explications. "
                    "Il suit généralement la règle des 5W (Who, What, When, Where, Why)."
                ),
                medias="genre_d_information.mp3",
                est_vue=0,
                id_cours=cours2.id,
            ),
            models.Page(
                description="Description 3",
                content=(
                    "La brève : Un texte court (5 à 10 lignes) qui donne une information essentielle sans commentaire. "
                    "L'article de presse : Développe un sujet avec des détails et des explications. "
                    "Il suit généralement la règle des 5W (Who, What, When, Where, Why)."
                ),
                medias="genre_opinion.mp4",
                est_vue=0,
                id_cours=cours2.id,
            ),
        ]
        for p in pages_cours2:
            db.add(p)

        qcms_cours2 = [
            models.QCM(
                question="Quel format journalistique donne une information essentielle en 5 à 10 lignes sans commentaire ?",
                rep1="L'éditorial",
                rep2="La brève",
                rep3="Le reportage",
                rep4="Le portrait",
                soluce=2,
                id_cours=cours2.id,
            ),
            models.QCM(
                question="Que représente le 'W' de 'Why' dans la règle des 5W ?",
                rep1="La date de publication",
                rep2="Le lieu de l'événement",
                rep3="La raison ou la cause de l'événement",
                rep4="Le nom du journaliste",
                soluce=3,
                id_cours=cours2.id,
            ),
            models.QCM(
                question="Quelle est la principale différence entre une brève et un article de presse ?",
                rep1="La brève contient des photos, l'article non",
                rep2="La brève est plus longue que l'article",
                rep3="La brève est courte et factuelle, l'article développe et explique",
                rep4="L'article est publié uniquement en ligne",
                soluce=3,
                id_cours=cours2.id,
            ),
        ]
        for q in qcms_cours2:
            db.add(q)

        db.commit()
        print(f"Cours 2 créé : {cours2.titre} — {len(pages_cours2)} pages, {len(qcms_cours2)} QCM")

        print("\n✅ Seed terminé avec succès.")

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors du seed : {e}")
        raise
    finally:
        with suppress(Exception):
            db.close()


if __name__ == "__main__":
    seed_cours()