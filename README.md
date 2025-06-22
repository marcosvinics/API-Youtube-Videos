# 📺 YouTube API Wrapper

Este projeto é uma API simples construída com Flask que interage com o YouTube Data API v3. Ela permite:

- Obter o vídeo mais recente de um canal
- Buscar vídeos específicos pelo título
- Encontrar playlists de um canal pelo nome

Ideal para ser usada como backend em aplicações que exibem vídeos ou playlists dinamicamente.

---

## 🌐 Funcionalidades

- `GET /video_recente`: Retorna o vídeo mais recente do canal
- `GET /video?titulo=<titulo>`: Retorna o link de um vídeo com base no título buscado
- `GET /playlist?nome=<nome>`: Busca playlists por nome
- `GET /`: Exibe instruções básicas da API

---

## 🚀 Deploy (Vercel + Google Cloud)

### 1. **Obtenha uma chave da YouTube Data API**
- Vá até [Google Cloud Console](https://console.cloud.google.com/)
- Crie um projeto ou use um existente
- Ative a **YouTube Data API v3**
- Gere uma chave de API

### 2. **Configure as variáveis de ambiente**

No painel da Vercel:

- `MY_SECRET_TOKEN`: sua API Key do YouTube
- `CHANNEL_ID`: ID do canal do YouTube

> ❗️Essas variáveis são obrigatórias para o funcionamento da API.

### 3. **Deploy no Vercel**

- Clone este repositório
- Faça login no Vercel (`vercel login`)
- Rode `vercel --prod` para fazer o deploy

> Certifique-se de que o `vercel.json` (caso esteja usando) esteja configurado corretamente para rodar com Flask via Python.

---

## 🔍 Exemplos de uso

### Obter vídeo mais recente:
GET https://sua-api.vercel.app/video_recente

### Buscar vídeo por título:
GET https://sua-api.vercel.app/video?titulo=nome+do+video

### Buscar playlists por nome:
GET https://sua-api.vercel.app/playlist?nome=nome+da+playlist

---

## 🛠 Requisitos de execução local

- Python 3.10+
- Flask
- `requests` (`pip install flask requests`)

### Executar localmente:
```bash
export MY_SECRET_TOKEN='sua-api-key'
export CHANNEL_ID='id-do-canal'
python app.py
