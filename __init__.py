from flask import Flask, render_template, request, redirect, url_for, session
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

@app.route('/')
def home():
    if not est_authentifie():  # Vérifier si l'utilisateur est authentifié
        return redirect(url_for('authentification'))  # Si non, rediriger vers la page de connexion
    return render_template('home.html')  # Si oui, afficher la page d'accueil



@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vérifier les identifiants
        if username in utilisateurs and utilisateurs[username]["password"] == password:
            session['authentifie'] = True  # Marquer l'utilisateur comme authentifié
            session['role'] = utilisateurs[username]["role"]  # Stocker le rôle
            session['utilisateur_id'] = username  # Stocker l'identifiant utilisateur
            return redirect(url_for('home'))  # Rediriger vers la page d'accueil

        # Si les identifiants sont incorrects, afficher une erreur
        return render_template('formulaire_authentification.html', error=True)

    # Afficher le formulaire de connexion
    return render_template('formulaire_authentification.html', error=False)


@app.route('/logout')
def logout():
    session.clear()  # Effacer la session de l'utilisateur
    return redirect(url_for('authentification'))  # Rediriger vers la page de connexion


# Route pour gérer les livres (Affichage des livres, Ajout, Suppression et Recherche)
@app.route('/livres', methods=['GET', 'POST'])
def gerer_livres():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Recherche de livres
    recherche = request.form.get('recherche')
    if recherche:
        cursor.execute("SELECT * FROM Livres WHERE Titre LIKE ? OR Auteur LIKE ?", (f'%{recherche}%', f'%{recherche}%'))
    else:
        cursor.execute('SELECT * FROM Livres')
    livres = cursor.fetchall()

    if request.method == 'POST' and est_admin():
        if 'ajouter_stock' in request.form:
            livre_id = request.form['livre_id']
            quantite_ajoutee = request.form['quantite']
            cursor.execute('UPDATE Livres SET Quantite = Quantite + ? WHERE ID_livre = ?', (quantite_ajoutee, livre_id))
            conn.commit()
        
        if 'ajouter_livre' in request.form:
            titre = request.form['titre']
            auteur = request.form['auteur']
            annee = request.form['annee']
            quantite = request.form['quantite']
            cursor.execute('INSERT INTO Livres (Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?)', 
                           (titre, auteur, annee, quantite))
            conn.commit()

        if 'supprimer_livre' in request.form:
            livre_id = request.form['livre_id']
            cursor.execute('DELETE FROM Livres WHERE ID_livre = ?', (livre_id,))
            conn.commit()

    conn.close()
    return render_template('livres.html', livres=livres, role=session.get('role'))

# Route pour emprunter un livre
@app.route('/emprunter/<int:id_livre>', methods=['POST'])
def emprunter_livre(id_livre):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT Quantite FROM Livres WHERE ID_livre = ?', (id_livre,))
    livre = cursor.fetchone()
    if livre and livre[0] > 0:
        cursor.execute('UPDATE Livres SET Quantite = Quantite - 1 WHERE ID_livre = ?', (id_livre,))
        cursor.execute('INSERT INTO Emprunts (ID_utilisateur, ID_livre) VALUES (?, ?)', (session['utilisateur_id'], id_livre))
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

    cursor.execute('SELECT ID_livre FROM Emprunts WHERE ID_emprunt = ?', (id_emprunt,))
    emprunt = cursor.fetchone()
    if emprunt:
        cursor.execute('UPDATE Livres SET Quantite = Quantite + 1 WHERE ID_livre = ?', (emprunt[0],))
        cursor.execute('UPDATE Emprunts SET Statut = "Terminé", Date_retour = DATE("now") WHERE ID_emprunt = ?', (id_emprunt,))
        conn.commit()

    conn.close()
    return redirect(url_for('mes_emprunts'))

# Route pour afficher tous les emprunts (Admin seulement)
@app.route('/emprunts', methods=['GET'])
def voir_emprunts():
    if not est_authentifie() or not est_admin():
        return "<h2>Accès refusé : vous devez être administrateur pour voir les emprunts.</h2>", 403

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT E.ID_emprunt, E.ID_utilisateur, L.Titre, L.Auteur, E.Date_emprunt, E.Date_retour, E.Statut
        FROM Emprunts E
        JOIN Livres L ON E.ID_livre = L.ID_livre
        WHERE E.Statut != "Terminé"
    ''')
    emprunts = cursor.fetchall()
    conn.close()

    return render_template('emprunts.html', emprunts=emprunts)

if __name__ == "__main__":
    app.run(debug=True)
