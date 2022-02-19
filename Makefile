IMAGE = gwent-image-parser
WEB = gwent-web

build:
  docker build -t $(IMAGE) ./$(IMAGE) --platform linux/x86_64
  docker network create $(WEB)
 
run:
  docker-compose up
 
.PHONY: build run