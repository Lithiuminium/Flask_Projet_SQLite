-- Table des livres
CREATE TABLE Livres (
    ID_livre INTEGER PRIMARY KEY AUTOINCREMENT,
    Titre TEXT NOT NULL,
    Auteur TEXT NOT NULL,
    Annee_publication INTEGER,
    Quantite INTEGER NOT NULL
);

-- Table des utilisateurs
CREATE TABLE Utilisateurs (
    ID_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom TEXT NOT NULL,
    Prenom TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Mot_de_passe TEXT NOT NULL,
    Role TEXT CHECK (Role IN ('Admin', 'User')) NOT NULL DEFAULT 'User'
);

-- Table des emprunts
CREATE TABLE Emprunts (
    ID_emprunt INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_utilisateur INTEGER NOT NULL,
    ID_livre INTEGER NOT NULL,
    Date_emprunt DATE NOT NULL DEFAULT (DATE('now')),
    Date_retour DATE,
    Statut TEXT CHECK (Statut IN ('En cours', 'Terminé')) NOT NULL DEFAULT 'En cours',
    FOREIGN KEY(ID_utilisateur) REFERENCES Utilisateurs(ID_utilisateur),
    FOREIGN KEY(ID_livre) REFERENCES Livres(ID_livre)
);
