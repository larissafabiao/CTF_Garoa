#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Iniciando deploy da aplicação...${NC}"

# Verifica se o Swarm já está inicializado
if ! docker info | grep -q "Swarm: active"; then
    echo -e "${GREEN}Inicializando Docker Swarm...${NC}"
    docker swarm init
else
    echo -e "${GREEN}Swarm já está ativo${NC}"
fi

# Remove a stack existente se houver
echo -e "${GREEN}Removendo stack anterior se existir...${NC}"
docker stack rm challenge_stack 2>/dev/null
echo "Aguardando 10 segundos para garantir que todos os serviços foram removidos..."
sleep 10

# Criar rede overlay se não existir
if ! docker network ls | grep -q "ai_network"; then
    echo -e "${GREEN}Criando rede ai_network...${NC}"
    docker network create -d overlay ai_network
fi

# Build das imagens
echo -e "${GREEN}Construindo imagens Docker...${NC}"
docker build -t app_service:latest -f Dockerfile .

# Deploy da stack
echo -e "${GREEN}Deployando stack...${NC}"
docker stack deploy -c docker-compose.yml challenge_stack

# Verificar status
echo -e "${GREEN}Verificando status dos serviços...${NC}"
sleep 5
docker stack services challenge_stack

echo -e "${GREEN}Deploy finalizado!${NC}"
echo -e "${GREEN}Para verificar os logs, use: docker service logs challenge_stack_app${NC}"