from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Dictionnaire des utilisateurs pour l'authentification (ajout d'un rôle Admin/User)
utilisateurs = {
    "admin": {"password": "admin123", "role": "Admin"},
    "user": {"password": "12345", "role": "User"}
}

# Fonction pour vérifier si un utilisateur est authentifié
def est_authentifie():
    return session.get('authentifie', False)

# Fonction pour vérifier si l'utilisateur est admin
def est_admin():
    return session.get('role') == 'Admin'

# Route principale
@app.route('/')
def home():
    return render_template('home.html')

# Route pour l'authentification
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Récupérer les informations de connexion
        username = request.form['username']
        password = request.form['password']
        
        # Vérification des identifiants
        if username in utilisateurs and utilisateurs[username]["password"] == password:
            session['authentifie'] = True
            session['role'] = utilisateurs[username]["role"]
            return redirect(url_for('home'))

        return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

# Route pour la déconnexion
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('authentification'))

# Route pour consulter les clients
@app.route('/clients')
def consultation_clients():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    clients = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', clients=clients)

# Routes pour gérer les livres
@app.route('/livres', methods=['GET', 'POST'])
def gerer_livres():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        if not est_admin():
            return "<h2>Accès refusé : vous devez être administrateur pour ajouter des livres.</h2>", 403

        # Ajouter un nouveau livre
        titre = request.form['titre']
        auteur = request.form['auteur']
        annee = request.form['annee']
        quantite = request.form['quantite']

        cursor.execute(
            'INSERT INTO Livres (Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?)',
            (titre, auteur, annee, quantite)
        )
        conn.commit()

    # Récupérer tous les livres
    cursor.execute('SELECT * FROM Livres')
    livres = cursor.fetchall()
    conn.close()

    return render_template('livres.html', livres=livres, role=session.get('role'))

# Route pour emprunter un livre
@app.route('/emprunter/<int:id_livre>', methods=['POST'])
def emprunter_livre(id_livre):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Vérifier la disponibilité du livre
    cursor.execute('SELECT Quantite FROM Livres WHERE ID_livre = ?', (id_livre,))
    livre = cursor.fetchone()
    if livre and livre[0] > 0:
        # Réduire la quantité et enregistrer l'emprunt
        cursor.execute('UPDATE Livres SET Quantite = Quantite - 1 WHERE ID_livre = ?', (id_livre,))
        cursor.execute(
            'INSERT INTO Emprunts (ID_utilisateur, ID_livre) VALUES (?, ?)',
            (session['utilisateur_id'], id_livre)
        )
        conn.commit()

    conn.close()
    return redirect(url_for('gerer_livres'))

# Route pour retourner un livre
@app.route('/retour/<int:id_emprunt>', methods=['POST'])
def retourner_livre(id_emprunt):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Marquer l'emprunt comme terminé
    cursor.execute('SELECT ID_livre FROM Emprunts WHERE ID_emprunt = ?', (id_emprunt,))
    emprunt = cursor.fetchone()
    if emprunt:
        cursor.execute('UPDATE Livres SET Quantite = Quantite + 1 WHERE ID_livre = ?', (emprunt[0],))
        cursor.execute('UPDATE Emprunts SET Statut = "Terminé", Date_retour = DATE("now") WHERE ID_emprunt = ?', (id_emprunt,))
        conn.commit()

    conn.close()
    return redirect(url_for('gerer_livres'))

# Route pour afficher les emprunts de l'utilisateur
@app.route('/mes_emprunts')
def mes_emprunts():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Emprunts WHERE ID_utilisateur = ?', (session['utilisateur_id'],))
    emprunts = cursor.fetchall()
    conn.close()

    return render_template('mes_emprunts.html', emprunts=emprunts)

if __name__ == "__main__":
    app.run(debug=True)
