import sqlite3

def init_db():
    connection = sqlite3.connect('database.db')

    with connection:
        # Exécuter le script SQL pour créer les tables
        connection.executescript('''
        CREATE TABLE IF NOT EXISTS clients (
            ID_client INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            adresse TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Livres (
            ID_livre INTEGER PRIMARY KEY AUTOINCREMENT,
            Titre TEXT NOT NULL,
            Auteur TEXT NOT NULL,
            Annee_publication INTEGER,
            Quantite INTEGER NOT NULL CHECK (Quantite >= 0)
        );

        CREATE TABLE IF NOT EXISTS Emprunts (
            ID_emprunt INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_utilisateur TEXT NOT NULL,
            ID_livre INTEGER NOT NULL,
            Date_emprunt DATE NOT NULL DEFAULT (DATE('now')),
            Date_retour DATE,
            Statut TEXT NOT NULL DEFAULT 'Actif',
            FOREIGN KEY (ID_livre) REFERENCES Livres (ID_livre)
        );
        ''')

        # Ajouter quelques données de test pour les livres
        connection.executemany(
            'INSERT INTO Livres (Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?)',
            [
                ("1984", "George Orwell", 1949, 5),
                ("Le Petit Prince", "Antoine de Saint-Exupéry", 1943, 3),
                ("Harry Potter à l'école des sorciers", "J.K. Rowling", 1997, 7),
                ("Les Misérables", "Victor Hugo", 1862, 4),
                ("L'Alchimiste", "Paulo Coelho", 1988, 6)
            ]
        )

    print("Base de données initialisée avec succès.")

if __name__ == "__main__":
    init_db()
