docker-build:
	docker build -t ranaas/hw3:latest .

docker-push:
	docker push ranaas/hw3:latest

docker-run-dev:
	docker run -p 5000:80 ranaas/hw3:latest 

docker-run-prod:
	docker run -p 8081:80 ranaas/hw3:latest 

docker-run-it:
	docker run -ti ranaas/hw3:latest sh
