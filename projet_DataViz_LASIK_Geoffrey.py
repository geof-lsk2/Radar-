# Importation des bibliothèques

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px

csv_url = "https://static.data.gouv.fr/resources/jeu-de-donnees-des-vitesses-pratiquees-issues-des-voitures-radars-a-conduite-externalisee/20221221-161623/opendata-vitesse-2021-01-01-2021-12-31.csv"

# Téléchargement des données
def load_data():
    data = pd.read_csv(csv_url, delimiter = ';')
    return data

df = load_data()

# On ne prend qu'une partie du dataset car ce dernier comporte trop de lignes.
# On peut en prendre seulement 10 % sans que cela gêne la lecture et les analyses.

sample_df = df.sample(frac=0.01, random_state=42)

# Création des colonnes temporelles à partir de la colonne date

sample_df['date'] = pd.to_datetime(sample_df['date'], format='%Y-%m-%dT%H:%M')
sample_df['jour_de_la_semaine'] = sample_df['date'].dt.day_name()
sample_df['jour_du_mois'] = sample_df['date'].dt.day
sample_df['mois'] = sample_df['date'].dt.month_name()
sample_df['saison'] = sample_df['date'].dt.month.map({1: 'Hiver', 2: 'Hiver', 3: 'Printemps', 4: 'Printemps', 5: 'Printemps', 6: 'Été', 7: 'Été', 8: 'Été', 9: 'Automne', 10: 'Automne', 11: 'Automne', 12: 'Hiver'})
sample_df['heure_du_jour'] = sample_df['date'].dt.strftime('%H:%M')
sample_df['surplus_reglementation'] = sample_df['mesure'] - sample_df['limite']

# Création de la colonne 'surplus_reglementation' à l'aide d'une fonction
def statut_infraction(surplus_reglementation):
    if surplus_reglementation > 0:
        return 'infraction'
    else:
        return 'innocent'


sample_df['En tort'] = sample_df['surplus_reglementation'].apply(statut_infraction)

# Création de la sidebar
with st.sidebar:
    st.image("images.png", width=300)
    st.markdown("# Informations générales ")
    st.markdown("**Geoffrey LASIK**")
    st.markdown("BIA1")
    st.markdown("Date : 23/10/2023")
    st.markdown("#datavz2023efrei")
    st.markdown('https://www.linkedin.com/in/geoffrey-lasik-stage-novembre-2023-datascience/')

# Premières informations de la page d'accueil

st.title("La sécurité routière, ou que font réellement les radars ? ")
st.image('642eca4f56bfe2117ccf4307_89705bf2-c4fe-4966-bdee-fdd306c642b3_radar-autoroute.jpeg', caption='Gendarmes ou conducteurs, ce site Web est fait pour vous ! Je vous invite donc à descendre votre souris.', use_column_width=True)

# Texte d'introduction

intro_text = """
Bienvenue sur notre analyse des excès de vitesse : Comprendre les Facteurs Temporels des Excès de Vitesse.

L'excès de vitesse sur les routes est un problème de sécurité routière majeur, mais saviez-vous que les facteurs temporels peuvent jouer un rôle crucial dans sa fréquence et sa gravité ? Notre analyse explore les données sur les excès de vitesse tout au long de l'année 2021 pour comprendre les tendances et les variations.
"""
st.write(intro_text)

# Aperçu optionnel du jeu de données

if st.checkbox("Cochez si vous souhaitez obtenir une vue plus détaillée des données utilisées"):
    st.subheader("Aperçu du jeu de données")
    st.write(sample_df.head())

# Suite du texte d'introduction

a = """Nous nous pencherons sur la question : "Quels sont les facteurs temporels qui peuvent influencer les excès de vitesse ?" Découvrez les réponses à travers des graphiques, des statistiques et des informations précieuses qui vous aideront à mieux comprendre les tendances liées à la vitesse et à la sécurité routière.
"""
st.write(a)

# Histogrammes et relevés optionnels si l'utilisateur sélectionne la colonne

st.write('Pour les plus curieux et volontaires, je vous laisse observer des histogrammes et relevés pour chaque colonne de nos données.')
selected_column = st.selectbox("Sélectionnez une colonne :", [""] + list(sample_df.columns)[2:])
if selected_column:
    st.subheader(f"Vous avez choisi : {selected_column}")
    if sample_df[selected_column].dtype == "object":
        if selected_column == 'mois':
            st.subheader("Relevés par mois")
            cpt_mois= sample_df[selected_column].value_counts()
            st.bar_chart(cpt_mois)
        elif selected_column == 'jour_de_la_semaine':
            st.subheader("Relevés par jour de la semaine")
            cpt_jour = sample_df[selected_column].value_counts()
            st.bar_chart(cpt_jour)
        elif selected_column == 'saison':
            st.subheader("Répartition par saison")
            cpt_saison = sample_df[selected_column].value_counts()
            st.bar_chart(cpt_saison)
        elif selected_column == 'heure_du_jour':
            st.subheader("Répartition par heure du jour")
            cpt_heure = sample_df[selected_column].value_counts()
            st.bar_chart(cpt_heure)
        elif selected_column == 'jour_du_mois':
            st.subheader("Répartition par jour du mois")
            cpt_jour2 = sample_df[selected_column].value_counts()
            st.bar_chart(cpt_jour2)
    else:
        fig, ax = plt.subplots()
        plt.hist(sample_df[selected_column], bins=60)
        st.pyplot(fig)

# Lancement du premier constat censé commencer véritablement l'histoire

innocent_count = sample_df['En tort'].value_counts().get('innocent', 0)
infraction_count = sample_df['En tort'].value_counts().get('infraction', 0)
st.subheader("Premier constat : Répartition des excès de vitesse")
data = pd.DataFrame({'Catégorie': ['innocent', 'infraction'], 'Nombre': [innocent_count, infraction_count]})
fig = px.pie(data, names='Catégorie', values='Nombre')
st.plotly_chart(fig)

# On s'intéresse désormais à la temporalité des excès de vitesse

st.title('Des infractions, oui, mais quand ?')
filtered_data = sample_df[sample_df['En tort'] == 'infraction']

# Infractions par saison

st.subheader(' 1) Répartition des infractions par saison')
fig = px.bar(filtered_data, x='saison', title="Répartition des infractions par saison", labels={'saison': 'Saison', 'count': 'Nombre d\'infractions'})
st.plotly_chart(fig)

# Infractions par mois

st.subheader(' 2) Répartition des infractions par mois')
fig = px.bar(filtered_data, x='mois', title="Répartition des infractions par mois", labels={'mois': 'Mois', 'count': 'Nombre d\'infractions'})
st.plotly_chart(fig)

# Infractions par jour de la semaine

st.subheader(' 3) Répartition des infractions par jour de la semaine')
fig = px.bar(filtered_data, x='jour_de_la_semaine', title="Répartition des infractions par jour de la semaine", labels={'jour_de_la_semaine': 'Jour de la semaine', 'count': 'Nombre d\'infractions'})
st.plotly_chart(fig)

# Carte de chaleur sur les infractions
st.subheader('Carte de chaleur de la répartition des infractions par jour de la semaine et heure du jour')
pivot_table = filtered_data.pivot_table(index='jour_de_la_semaine', columns='heure_du_jour', values='En tort', aggfunc='count')
fig, ax = plt.subplots()
sns.heatmap(pivot_table, cmap='YlGnBu', ax=ax, cbar_kws={'label': 'Nombre d\'infractions'})
ax.set_xlabel('Heure du jour')
ax.set_ylabel('Jour de la semaine')
st.pyplot(fig)
mot = """Interprétation : Plus c'est bleu ou foncé et plus il y a d'infractions."""
st.write(mot)

# On s'intéresse maintenant à la vitesse des excès

st.title('Des infractions, oui, mais à quelle vitesse ?')

# Tranche des excès

sample_df['tranche_excès'] = pd.cut(sample_df['surplus_reglementation'], bins=[0, 5, 10, 15, 20, 25, 30, 35], labels=['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-35'])
st.subheader('Répartition des infractions par tranche d\'excès de vitesse')
fig, ax = plt.subplots()
sns.set(font_scale=0.8)
sns.countplot(data=sample_df[sample_df['En tort'] == 'infraction'], x='tranche_excès', ax=ax)
ax.set_xlabel('Tranche d\'excès de vitesse')
ax.set_ylabel("Nombre d'infractions")
plt.xticks(rotation=45)
st.pyplot(fig)

mot = """À noter qu'il existe une marge d'erreur sur les mesures des radars. 
Cela signifie qu'un excès de vitesse à moins de 5 km/h sur une route limitée à 90 correspond à un excès de vitesse en théorie, mais qui n'engendrera pas d'amende pour vous. """
st.write(mot)

# Répartition circulaire des vitesses

parts = 15
top_parts = sample_df['surplus_reglementation'].value_counts().head(parts)
filtered_data = sample_df[sample_df['surplus_reglementation'].isin(top_parts.index)]
st.subheader('Diagramme circulaire de la répartition des excès de vitesse (ou pas)')
fig = px.pie(filtered_data, names='surplus_reglementation', hole=0.3, width=800, height=600)
fig.update_layout(legend_title_text='Surplus de reglementation')
st.plotly_chart(fig)

mot = """Vous l'aurez compris, les chiffres négatifs indiquent une vitesse respectant la limitation et les chiffres positifs indiquent le surplus d'excès de vitesse.
À noter que seules les 15 vitesses les plus fréquentes sont relevés."""
st.write(mot)

# Jeu de fin

st.title('Finissons par un jeu intéractif pour vous !')
st.image('avousdejouer.jpg')
texte = """Il s'agit d'un jeu spécialement fait pour vous ! 
Vous prévoyez de sortir en voiture tel jour à telle heure ? Remplissez ce jour et regardez précisément le nombre d'infractions qui auront lieu durant votre trajet.
Vous pouvez également vous amuser à compter les voitures qui seront en excès de vitesse ? 
Quoi qu'il arrive, soyez prudents !
"""
st.write(texte)

st.subheader('Histogramme du nombre d\'infractions par heure pour un jour de la semaine choisi par vous-même')
selected_day = st.selectbox('Sélectionnez un jour de la semaine', sample_df['jour_de_la_semaine'].unique())
filtered_data = sample_df[(sample_df['jour_de_la_semaine'] == selected_day) & (sample_df['En tort'] == 'infraction')]

histogram = alt.Chart(filtered_data).mark_bar().encode(
    x=alt.X('heure_du_jour:O', title='Heure du jour'),
    y=alt.Y('count()', title='Nombre d\'infractions'),
    tooltip=['heure_du_jour:N', 'count()']
).properties(
    width=700,
    height=500
)
st.altair_chart(histogram)

# Conclusion de fin

conclusion = """J'espère que cette étude vous aura plû. 
Son objectif était de vous faire comprendre et prendre conscience des enjeux de la sécurité routière, et de comprendre davantage la fréquence des excès de vitesse.
Cette étude s'est voulu intéractive pour vous, car nous estimons que c'est la base pour apprendre davantage sur des sujets sociétaux comme celui-ci. 
Nous essaierons également d'ajouter dans notre base de données les localisations (régions, départements, villes) pour vous fournir d'autres visualisations.
En attendant, à vos questionnements, et surtout, prudence sur les routes !"""
st.write(conclusion)
