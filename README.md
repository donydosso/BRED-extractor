# BRED-extractor

**BRED-extractor** est une application web conçue pour extraire et analyser des données spécifiques. Elle combine des composants backend en Python et Go avec une interface utilisateur moderne. Le projet est entièrement conteneurisé à l'aide de Docker et Docker Compose, facilitant ainsi le déploiement et l'exécution.

## Fonctionnalités

* Extraction de données à partir de sources spécifiques.
* Analyse et traitement des données extraites.
* Interface utilisateur interactive pour visualiser les résultats.
* Conteneurisation complète avec Docker.
* Scripts Makefile pour automatiser les tâches courantes.
* Possibilité d'exposer l'application localement via ngrok.

## Prérequis

* [Docker](https://www.docker.com/) installé sur votre machine.
* [Docker Compose](https://docs.docker.com/compose/) pour orchestrer les conteneurs.
* [Make](https://www.gnu.org/software/make/) pour utiliser le Makefile.
* [Ngrok](https://ngrok.com/) pour exposer l'application localement.

## Installation

1. Clonez le dépôt :

```bash
git clone https://github.com/donydosso/BRED-extractor.git
cd BRED-extractor
```

2. Construisez et démarrez les conteneurs :

```bash
make build
make up
```

Cela construira les images Docker et démarrera les services définis dans `docker-compose.yml`.

3. Accédez à l'application via votre navigateur à l'adresse :

```
http://localhost:8080
```

## Utilisation du Makefile

Le projet inclut un `Makefile` pour simplifier les commandes Docker courantes :

* `make build` : Construit les images Docker.
* `make up` : Démarre les conteneurs en arrière-plan.
* `make down` : Arrête et supprime les conteneurs.
* `make logs` : Affiche les logs des conteneurs.
* `make restart` : Redémarre les conteneurs.

## Exposer l'application avec ngrok

Ngrok permet d'exposer votre application locale à Internet. Voici comment l'utiliser :

1. Installez ngrok en suivant les instructions sur le site officiel :
   [https://ngrok.com/download](https://ngrok.com/download)

2. Connectez ngrok à votre compte :

```bash
ngrok config add-authtoken VOTRE_AUTHTOKEN
```

Remplacez `VOTRE_AUTHTOKEN` par le token fourni dans votre tableau de bord ngrok.

3. Démarrez un tunnel vers votre application :

```bash
ngrok http 8443
```

Ngrok vous fournira une URL publique (par exemple, `https://abcd1234.ngrok.io`) que vous pouvez partager pour accéder à votre application depuis n'importe où.

## Structure du projet

```bash
BRED-extractor/
├── certs/             # Certificats SSL
├── frontend/          # Fichiers frontend (HTML, CSS, JS)
├── go/                # Code backend en Go
├── python/            # Scripts Python pour l'extraction/analyse
├── Dockerfile         # Fichier Docker pour l'application
├── docker-compose.yml # Configuration Docker Compose
├── Makefile           # Scripts Makefile pour automatiser les tâches
└── README.md          # Ce fichier
```

## Contributions

Les contributions sont les bienvenues ! N'hésitez pas à forker le projet, créer une branche, apporter vos modifications et soumettre une pull request.
