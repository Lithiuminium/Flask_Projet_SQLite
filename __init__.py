from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour vérifier si l'utilisateur est authentifié
def est_authentifie():
    return session.get('authentifie')

# Fonction pour vérifier si l'utilisateur est un utilisateur avec un login spécifique
def est_utilisateur():
    return session.get('utilisateur')

# Fonction de connexion à la base de données SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Retourner les résultats sous forme de dictionnaires
    return conn

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))  # Redirige vers la page d'authentification si non authentifié

    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Vérification des identifiants
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # à améliorer avec un mot de passe haché
            session['authentifie'] = True
            return redirect(url_for('lecture'))
        elif username == 'user' and password == '12345':
            session['utilisateur'] = True  # Marquer l'utilisateur comme authentifié avec un rôle utilisateur
            return redirect(url_for('fiche_nom'))  # Rediriger vers la route de recherche du client
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_nom/', methods=['GET', 'POST'])
def fiche_nom():
    if not est_utilisateur():  # Vérifier si l'utilisateur est authentifié en tant qu'utilisateur
        return redirect(url_for('authentification'))  # Rediriger vers la page d'authentification si l'utilisateur n'est pas connecté

    if request.method == 'POST':
        client_name = request.form['name']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE nom LIKE ?', ('%' + client_name + '%',))
        data = cursor.fetchall()
        conn.close()
        if data:
            return render_template('read_data.html', data=data)  # Afficher les résultats de la recherche
        else:
            return "<h3>Aucun client trouvé</h3>", 404

    return render_template('search_form.html')  # Formulaire de recherche

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchone()  # Utiliser fetchone car un ID unique
    conn.close()
    if data:
        return render_template('read_data.html', data=data)
    else:
        return "Client non trouvé", 404

@app.route('/consultation/')
def ReadBDD():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    if not est_authentifie():
        return redirect(url_for('authentification'))  # Protéger cette route également
    return render_template('formulaire.html')

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    if not est_authentifie():
        return redirect(url_for('authentification'))  # Vérification d'authentification

    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insérer le nouveau client dans la base de données
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    
    return redirect('/consultation/')  # Rediriger vers la page de consultation

if __name__ == "__main__":
    app.run(debug=True)
