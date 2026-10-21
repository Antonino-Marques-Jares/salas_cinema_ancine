![Mudança de número de salas ativas no Brasil ao longo dos anos](ancine_salas_cinema.jpg)

**Fonte:**

[![Gov BR](govbr.webp)](https://dados.gov.br/dados/conjuntos-dados/salas-de-exibicao-e-complexos-registrados-na-ancine)

**Autor:**
Antonino Marques Jares

**Atualizado em:** 
21/10/2026

# salas_cinema_ancine
Animações sobre quantidade de salas de cinema da ANCINE ativas por Estado ou Região entre menor ano (2014) ao ano mais atual constante em json da ancine

# Passo 1
Clone o projeto do GitHub

No terminal verifique em que diretório você está, ao executar o comando :

git clone https://github.com/Antonino-Marques-Jares/salas_cinema_ancine.git

o projeto será criado neste diretório

# Passo 2
Execute no terminal o comando abaixo para fazer as instalações nescessárias

pip install -r requirements.txt

# Passo 3
Crie pasta 'videos' e 'json' no projeto

Obs.: ancine.json guarda metadados que será utilizado no site para atualizar informações na pagina (https://www.areadetrampo.com.br/salas-de-cinema-da-ancine-ativas-no-brasil-entre-2014-e-2025/)

# Passo 4

Execute

python etl_atualizar_ancine_no_site.py

# Passo 5
Verifique os vídeos na pasta videos




