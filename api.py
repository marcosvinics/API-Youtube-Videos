from flask import Flask, jsonify, Response, request
import requests
import os
import difflib

app = Flask(__name__)

API_KEY = os.getenv('MY_SECRET_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
MAX_RESULTS_PER_PAGE = 5

if not API_KEY or not CHANNEL_ID:
    raise ValueError("API_KEY e CHANNEL_ID precisam ser definidos como variáveis de ambiente")

def obter_todas_playlists():
    playlists = []
    proxima_pagina = None
    while True:
        url = f'https://www.googleapis.com/youtube/v3/playlists?part=snippet&channelId={CHANNEL_ID}&maxResults={MAX_RESULTS_PER_PAGE}&key={API_KEY}'
        if proxima_pagina:
            url += f'&pageToken={proxima_pagina}'
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()
        except requests.exceptions.RequestException as erro:
            return Response(f"Erro ao buscar dados: {str(erro)}", mimetype='text/plain'), 500
        if resposta.status_code != 200:
            return []

        dados = resposta.json()
        if 'items' in dados:
            playlists.extend(dados['items'])
        if 'nextPageToken' in dados:
            proxima_pagina = dados['nextPageToken']
        else:
            break
    return playlists

@app.route('/')
def index():
    return Response(
        'Para testar a API, acesse as URLs:\n'
        '- /playlist\n'
        '- /video_recente\n'
        '- /video?titulo=<titulo_do_video>',
        mimetype='text/plain'
    ), 200

@app.route('/video_recente', methods=['GET'])
def obter_video_recente():
    url = f'https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&channelId={CHANNEL_ID}&maxResults=1&key={API_KEY}'
    resposta = requests.get(url)
    dados = resposta.json()

    if 'items' in dados and len(dados['items']) > 0:
        video = dados['items'][0]
        if 'videoId' in video['id']:
            video_id = video['id']['videoId']
            titulo_video = video['snippet']['title']
            url_video = f'https://www.youtube.com/watch?v={video_id}'
            return Response(f'{titulo_video}: {url_video} ', mimetype='text/plain')
        else:
            return Response("Nenhum vídeo encontrado", mimetype='text/plain'), 404
    else:
        return Response('Nenhum vídeo encontrado', mimetype='text/plain'), 404

@app.route('/playlist', methods=['GET'])
def obter_playlist():
    nome_playlist = request.args.get('nome')
    if nome_playlist:
        nome_playlist = nome_playlist.lower()
        todas_playlists = obter_todas_playlists()
        playlists_correspondentes = []

        # Busca por correspondências parciais
        for playlist in todas_playlists:
            titulo_playlist = playlist['snippet']['title'].lower()
            if nome_playlist in titulo_playlist:  # Verifica se o nome buscado está no título
                playlist_id = playlist['id']
                url_playlist = f'https://www.youtube.com/playlist?list={playlist_id}'
                playlists_correspondentes.append(f'{playlist["snippet"]["title"]}: {url_playlist}')

        if playlists_correspondentes:
            # Retorna apenas as playlists que correspondem ao nome
            return Response("\n".join(playlists_correspondentes), mimetype='text/plain')
        else:
            # Sugestões baseadas em similaridade
            sugestoes = difflib.get_close_matches(
                nome_playlist, [playlist['snippet']['title'].lower() for playlist in todas_playlists]
            )
            if sugestoes:
                return Response(
                    f'Nenhuma playlist exata encontrada. Sugestões: {", ".join(sugestoes)}',
                    mimetype='text/plain'
                ), 404
            else:
                return Response(
                    f'Nenhuma playlist encontrada para "{nome_playlist}" e nenhuma sugestão disponível.',
                    mimetype='text/plain'
                ), 404
    else:
        return Response(
            'Por favor, forneça o nome da playlist usando o parâmetro "nome".',
            mimetype='text/plain'
        ), 400

@app.route('/video', methods=['GET'])
def obter_video_especifico():
    titulo_video = request.args.get('titulo')
    if not titulo_video:
        return Response(
            'Por favor, forneça o título do vídeo usando o parâmetro "titulo".',
            mimetype='text/plain'
        ), 400

    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={CHANNEL_ID}&q={titulo_video}&type=video&maxResults=1&key={API_KEY}'
    resposta = requests.get(url)

    if resposta.status_code != 200:
        return Response(f'Erro ao buscar vídeo: {resposta.text}', mimetype='text/plain'), 500

    dados = resposta.json()
    if 'items' in dados and len(dados['items']) > 0:
        video = dados['items'][0]
        video_id = video['id']['videoId']
        titulo_video = video['snippet']['title']
        url_video = f'https://www.youtube.com/watch?v={video_id}'
        return Response(f'{titulo_video}: {url_video}', mimetype='text/plain')
    else:
        return Response(
            f'Nenhum vídeo encontrado com o título "{titulo_video}".',
            mimetype='text/plain'
        ), 404

if __name__ == '__main__':
    app.run(debug=True)
