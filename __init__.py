from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Dictionnaire des utilisateurs pour l'authentification
utilisateurs = {
    "user": "12345"
}

# Fonction pour vérifier si un utilisateur est authentifié
def est_authentifie():
    return session.get('authentifie', False)

# Route principale
@app.route('/')
def hello_world():
    return render_template('hello.html')

# Route pour accéder à une page nécessitant une authentification
@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Récupérer les informations de connexion
        username = request.form['username']
        password = request.form['password']
        
        # Vérification des identifiants
        if username in utilisateurs and utilisateurs[username] == password:
            session['authentifie'] = True  # Marquer l'utilisateur comme authentifié
            return redirect(url_for('fiche_nom'))  # Rediriger directement vers fiche_nom

        # Si les identifiants sont incorrects
        return render_template('formulaire_authentification.html', error=True)

    # Afficher le formulaire d'authentification
    return render_template('formulaire_authentification.html', error=False)


# Route pour consulter les données dans la base de données
@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

# Route pour afficher le formulaire d'ajout de client
@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')

# Route pour enregistrer un nouveau client
@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')  # Redirection après enregistrement                                                                                                                                       

@app.route('/fiche_nom/', methods=['GET', 'POST'])
def fiche_nom():
    # Vérifiez si l'utilisateur est authentifié
    if not est_authentifie():
        return "<h2>Accès refusé : vous n'êtes pas authentifié.</h2>", 403
    
    resultats = []  # Initialise les résultats par défaut
    if request.method == 'POST':
        # Récupère le nom du formulaire
        nom_recherche = request.form.get('name')

        # Connectez-vous à la base et effectuez la requête
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Requête sécurisée pour éviter les injections SQL
        cursor.execute("SELECT nom, prenom, adresse FROM clients WHERE nom = ?", (nom_recherche,))
        resultats = cursor.fetchall()
        conn.close()

    # Rendre la page HTML et passer les résultats
    return render_template('fiche_nom.html', resultats=resultats)


if __name__ == "__main__":
    app.run(debug=True)
