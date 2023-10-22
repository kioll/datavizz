import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns 
import chardet
import numpy as np
import json

# Fonction pour charger les données
@st.cache_data
def load_data(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    
    # Détecter l'encodage
    char_encoding = chardet.detect(response.content)['encoding']
    
    # Décoder le contenu
    decoded_content = response.content.decode(char_encoding)
    
    # Lire le contenu avec pandas
    data = pd.read_csv(io.StringIO(decoded_content), delimiter=",", low_memory= False)
    
    return data




def main():
    

    st.title("Power Juice")

    # Charger les données
    url = "https://static.data.gouv.fr/resources/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/20231022-065434/consolidation-etalab-schema-irve-statique-v-2.2.0-20231021.csv"
    data = load_data(url)
    
    st.dataframe(data.head())
    # Convertir la date en datetime 
    data['date_mise_en_service'] = pd.to_datetime(data['date_mise_en_service'])


    


    # Styles CSS pour les boutons
    button_css = """
    <style>
        .button-style {
            background-color: #000000;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 12px;
        }
    </style>
    """

# Ajout des styles CSS à l'application
    st.markdown(button_css, unsafe_allow_html=True)

# Barre latérale avec boutons

# Ajoutez vos informations personnelles ici
    # Titre du menu
    st.sidebar.title("Menu")

    st.sidebar.markdown('<a href="#vis1" class="button-style">Aller à la Visualisation 1</a>', unsafe_allow_html=True)
    st.sidebar.markdown('<a href="#vis2" class="button-style">Aller à la Visualisation 2</a>', unsafe_allow_html=True)
    # Séparation visuelle
    st.sidebar.markdown("---")

    # Vos informations personnelles
    st.sidebar.markdown("## Mes liens")
    st.sidebar.markdown("   CUOC ENZO")
    st.sidebar.markdown("#DATAVIZ2023")
    st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/enzo-cuoc/)")
    st.sidebar.markdown("[GitHub](https://github.com/kioll)")
    
    

##############################

# viz 1 

     # Créer une ancre pour la Visualisation 1
    st.markdown("<a name='vis1'></a>", unsafe_allow_html=True)   
    
    # Assurez-vous que la colonne 'année' est bien en format int ou float et non pas en format string
    data['année'] = data['date_mise_en_service'].dt.year



    # Filtrer pour prendre seulement les données à partir de 2015
    df_filtré = data[data['année'] >= 2015]

    # Regroupement par année et comptage
    bornes_par_année = df_filtré.groupby('année').size()
  
    


    # Calcul du cumul
    bornes_cumulées = bornes_par_année.cumsum()
    # Ajoutez un titre au graphique en utilisant du code HTML
    st.markdown("<div style='text-align:center'><h3>Évolution du nombre de bornes de recharge</h3></div>", unsafe_allow_html=True)
    st.line_chart(bornes_cumulées, use_container_width=True)
    
    

###########################################################

#VIZ 2  
    import geopandas as gpd

    # Créer une ancre pour la Visualisation 2
    st.markdown("<a name='vis2'></a>", unsafe_allow_html=True)

    
    url = 'https://www.data.gouv.fr/fr/datasets/r/90b9341a-e1f7-4d75-a73c-bbc010c7feeb'

    # Charger les frontières des départements français
    france_map = gpd.read_file("departements.geojson")


    

    data['departement'] = data['consolidated_code_postal'].astype(str).str[:2]
    borne_count_by_departement = data.groupby('departement').size().reset_index(name='nb_bornes')

    merged = france_map.set_index('code').join(borne_count_by_departement.set_index('departement'))



   

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    merged.plot(column='nb_bornes', ax=ax, legend=True, cmap="YlGnBu", alpha=1,edgecolor='0.8')
    plt.title('Nombre de bornes de recharge par département')
    st.pyplot(fig)


#############################################################

#VIZ 3 
    data['gratuit'] = data['gratuit'].astype(str).str.lower()
    data['gratuit'] = data['gratuit'].map({"true": True, "false": False})
    # Remplacer les valeurs NaN par False dans la colonne 'gratuit'
    data['gratuit'].fillna(False, inplace=True)

    # Compter le nombre de bornes gratuites (où la colonne 'gratuit' est True) et payantes (où 'gratuit' est False)
    nb_gratuit = len(data[data['gratuit']])
    nb_payant = len(data[~data['gratuit']])

    import plotly.express as px

    # Créer un DataFrame pour la visualisation
    df_pie = pd.DataFrame({
        'Type': ['Gratuit', 'Payant'],
        'Nombre de bornes': [nb_gratuit, nb_payant]
    })

    # Créer le pie chart avec Plotly
    fig = px.pie(df_pie, values='Nombre de bornes', names='Type', title="Répartition des bornes gratuites et payantes")

    # Afficher le graphique avec Streamlit
    st.plotly_chart(fig)


######################################

#VIZ 4 


 

    # Nettoyer les valeurs des colonnes en les convertissant en booléens
    cols_to_clean = ['prise_type_ef', 'prise_type_2', 'prise_type_combo_ccs', 'prise_type_chademo']

    for col in cols_to_clean:
        data[col] = data[col].str.lower().map({'true': True, 'false': False})

    # Compter le nombre de "True" pour chaque type de prise
    prise_counts = data[cols_to_clean].sum()

   # Normalisation en pourcentage

    # Créer un graphique à barres
    fig = px.bar(x=cols_to_clean, y=prise_counts, labels={'x': 'Type de prise', 'y': 'Nombre de prises'},
                title='Comparaison des types de prises sur les bornes')

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig)

    
    
    
   


    


# Exécuter l'application principale
if __name__ == "__main__":
    main()
