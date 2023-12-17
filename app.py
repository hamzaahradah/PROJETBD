# app.py
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
from datetime import date
from sqlalchemy import text
import matplotlib.pyplot as plt


# Connexion à la base de données MySQL
engine = create_engine('mysql://root:@localhost:3306/gym')

# Fonction pour exécuter les requêtes SQL
# Fonction pour exécuter les requêtes SQL
def run_query(query):
    return pd.read_sql_query(query, engine)

# Page d'accueil
def home():
    st.title("Application de Gestion de Salle de Sport")
    st.markdown("Bienvenue dans notre application web pour gérer les activités d'une salle de sport.")
    st.markdown("Réalisé par AHRADAH Hamza")

def display_sessions():
    st.header("Affichage des Séances")

    # Obtenez la liste des types de séances uniques depuis la base de données
    session_types = run_query("SELECT DISTINCT Type FROM SEANCE")['Type'].tolist()

    # Widget de filtrage par type de séance
    selected_type = st.selectbox("Filtrer par type de séance:", session_types)

    # Widget de filtrage par niveau
    min_level, max_level = st.slider("Filtrer par plage de niveaux:", min_value=1, max_value=4, value=(1, 4))

    # Requête SQL pour récupérer les séances filtrées
    query = f"SELECT * FROM SEANCE WHERE Type = '{selected_type}' AND Niveau BETWEEN {min_level} AND {max_level}"
    result = run_query(query)

    # Affichage des résultats
    st.dataframe(result)

# Fonction pour afficher les entraîneurs
# Fonction pour afficher les entraîneurs
# Fonction pour afficher les entraîneurs
# Fonction pour afficher les entraîneurs
def display_trainers():
    st.header("Affichage des Entraîneurs")

    # Widget de filtrage par nom de famille
    last_name_filter = st.text_input("Filtrer par nom de famille de l'entraîneur:")

    # Widget de filtrage par date de naissance
    birth_date_filter = st.text_input("Filtrer par date de naissance de l'entraîneur (YYYY-MM-DD):")

    # Requête SQL pour récupérer les entraîneurs filtrés
    query = "SELECT * FROM ENTRAINEUR WHERE 1"  # Always true condition to start the query

    if last_name_filter:
        query += f" AND Nom LIKE '%{last_name_filter}%'"
    if birth_date_filter:
        query += f" AND Date_de_naissance = '{birth_date_filter}'"

    result = run_query(text(query))

    # Affichage des résultats
    st.dataframe(result)



# Fonction pour afficher les graphiques
def fetch_data():
    # Sample SQL queries (replace with your actual queries)
    query1 = "SELECT Nom, Niveau FROM SEANCE"
    query2 = "SELECT Jour, COUNT(*) AS Count FROM HORAIRE GROUP BY Jour"

    # Fetch data from the database
    data1 = pd.read_sql_query(query1, engine)
    data2 = pd.read_sql_query(query2, engine)

    return data1, data2

def display_charts():
    st.header("Affichage des Graphiques")

    # Fetch data from the database
    data_seance, data_horaire = fetch_data()

    # Bar chart for SEANCE table
    st.subheader("Bar Chart from SEANCE table")
    fig1, ax1 = plt.subplots()
    ax1.bar(data_seance['Nom'], data_seance['Niveau'])
    st.pyplot(fig1)

    # Bar chart for HORAIRE table
    st.subheader("Bar Chart from HORAIRE table")
    fig2, ax2 = plt.subplots()
    ax2.bar(data_horaire['Jour'], data_horaire['Count'])
    st.pyplot(fig2)

# Fonction pour insérer une nouvelle séance

def insert_new_session():
    st.header("Insertion d'une Nouvelle Séance")

    # Widgets pour le formulaire d'insertion
    session_name = st.text_input("Nom de la séance:")
    session_type = st.text_input("Type de la séance:")
    session_level = st.number_input("Niveau de la séance:", min_value=1, max_value=4)

    # Bouton d'insertion
    if st.button("Insérer la Séance"):
        try:
            # Préparez la requête SQL
            query = f"INSERT INTO SEANCE (Nom, Type, Niveau) VALUES ('{session_name}', '{session_type}', {session_level})"

            # Exécutez la requête SQL
            with engine.connect() as connection:
                connection.execute(text(query))
                connection.commit()

            st.success("Séance insérée avec succès!")
        except Exception as e:
            st.error(f"Erreur lors de l'insertion de la séance : {str(e)}")# Fonction pour insérer une nouvelle séance hebdomadaire
# ...
def insert_new_weekly_session():
    st.header("Insertion d'une Nouvelle Séance Hebdomadaire")

    # Widgets pour le formulaire d'insertion hebdomadaire
    trainers = run_query("SELECT CodeE FROM ENTRAINEUR")['CodeE'].tolist()
    trainer_code = st.selectbox("Code de l'entraîneur:", trainers)

    sessions = run_query("SELECT Id_S FROM SEANCE")['Id_S'].tolist()
    session_id = st.selectbox("ID de la séance:", sessions)

    day_of_week = st.selectbox("Jour de la semaine:", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"])

    start_time = st.time_input("Heure de début:")
    duration = st.number_input("Durée de la séance (en minutes):", min_value=1, max_value=60)
    gym_room = st.text_input("Salle de gym:")
    if st.button("Insérer la Séance hebdo"):
        # Vérifier les contraintes avant l'insertion
        if duration > 60:
            st.error("Erreur : La durée de la séance ne doit pas dépasser 60 minutes.")
        elif day_of_week not in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]:
            st.error("Erreur : Le jour de la semaine doit être compris entre le lundi et le vendredi.")
        elif run_query(f"SELECT * FROM HORAIRE WHERE Id_S = {session_id} AND Jour = '{day_of_week}'").shape[0] > 0:
            st.error("Erreur : Une séance est déjà programmée pour le même jour et la même séance.")
        else:
            try:
                # Préparez la requête SQL
                query = f"INSERT INTO HORAIRE (CodeE, Id_S, Jour, Heure_debut, Duree, Salle) VALUES ('{trainer_code}', '{session_id}', '{day_of_week}', '{start_time}', {duration}, '{gym_room}')"

                # Exécutez la requête SQL
                with engine.connect() as connection:
                    connection.execute(text(query))
                    connection.commit()

                st.success("Séance hebdomadaire insérée avec succès!")
            except Exception as e:
                st.error(f"Erreur lors de l'insertion de la séance hebdomadaire : {str(e)}")
# Appels aux fonctions en fonction de la page sélectionnée


# Menu de navigation
pages = {
    "Accueil": home,
    "Séances": display_sessions,
    "Entraîneurs": display_trainers,
    "Graphiques": display_charts,
    "Insertion de Séance": insert_new_session,
    "Insertion de Séance Hebdomadaire": insert_new_weekly_session,
}

# Barre de navigation
page = st.sidebar.radio("Navigation", list(pages.keys()))

# Exécution de la page sélectionnée
pages[page]()
