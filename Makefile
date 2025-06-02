# Build les deux images
build:
	docker-compose build

# Lancer les conteneurs via docker-compose
up:
	docker-compose up -d

# Arrêter les conteneurs
down:
	docker-compose down

# Voir les logs
logs:
	docker-compose logs -f

# Nettoyage
clean:
	docker system prune -f
