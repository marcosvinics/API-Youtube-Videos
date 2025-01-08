from flask import Flask, jsonify, Response, request
import requests
import os
import difflib

app = Flask(__name__)

API_KEY = os.getenv('MY_SECRET_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
MAX_RESULTS_PER_PAGE = 5

if not API_KEY or not CHANNEL_ID:
    raise ValueError("API_KEY and CHANNEL_ID must be set as environment variables")

def get_all_playlists():
    playlists = []
    next_page_token = None
    while True:
        url = f'https://www.googleapis.com/youtube/v3/playlists?part=snippet&channelId={CHANNEL_ID}&maxResults={MAX_RESULTS_PER_PAGE}&key={API_KEY}'
        if next_page_token:
            url += f'&pageToken={next_page_token}'
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response(f"Error fetching data: {str(e)}", mimetype='text/plain'), 500
        if response.status_code != 200:
            return []
        
        data = response.json()
        if 'items' in data:
            for item in data['items']:
                playlists.append(item)
        if 'nextPageToken' in data:
            next_page_token = data['nextPageToken']
        else:
            break
    return playlists

@app.route('/')
def index():
    return Response(
        'Para testar a API, acesse as URLs:\n'
        '- /playlists\n'
        '- /latest_video\n'
        '- /video?title=<titulo_do_video>',
        mimetype='text/plain'
    ), 200

@app.route('/latest_video', methods=['GET'])
def get_latest_video():
    url = f'https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&channelId={CHANNEL_ID}&maxResults=1&key={API_KEY}'
    response = requests.get(url)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        video_item = data['items'][0]
        if 'videoId' in video_item['id']:
            video_id = video_item['id']['videoId']
            video_title = video_item['snippet']['title']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            return Response(f'{video_title}: {video_url}', mimetype='text/plain')
        else:
            return Response("No video found", mimetype='text/plain'), 404
    else:
        return Response('No videos found', mimetype='text/plain'), 404

@app.route('/playlists', methods=['GET'])
def get_playlists():
    playlist_name = request.args.get('name')
    if playlist_name:
        playlist_name = playlist_name.lower()
        all_playlists = get_all_playlists()
        matched_playlists = []
        for playlist in all_playlists:
            item_name = playlist['snippet']['title'].lower()
            if playlist_name in item_name:
                playlist_id = playlist['id']
                playlist_url = f'https://www.youtube.com/playlist?list={playlist_id}'
                matched_playlists.append(f'{item_name}: {playlist_url}')
        if matched_playlists:
            return Response("\n".join(matched_playlists), mimetype='text/plain')
        else:
            suggestions = difflib.get_close_matches(
                playlist_name, [playlist['snippet']['title'].lower() for playlist in all_playlists]
            )
            return Response(
                f'Playlist not found. Suggestions: {", ".join(suggestions)}',
                mimetype='text/plain'
            ), 404
    else:
        all_playlists = get_all_playlists()
        playlists = []
        for playlist in all_playlists:
            playlist_id = playlist['id']
            playlist_title = playlist['snippet']['title']
            playlist_url = f'https://www.youtube.com/playlist?list={playlist_id}'
            playlists.append(f'{playlist_title}: {playlist_url}')
        return Response("\n".join(playlists), mimetype='text/plain')

@app.route('/video', methods=['GET'])
def get_specific_video():
    video_query = request.args.get('title')
    if not video_query:
        return Response(
            'Please provide a video title using the "title" query parameter.',
            mimetype='text/plain'
        ), 400

    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={CHANNEL_ID}&q={video_query}&type=video&maxResults=1&key={API_KEY}'
    response = requests.get(url)

    if response.status_code != 200:
        return Response(f'Error fetching video: {response.text}', mimetype='text/plain'), 500

    data = response.json()
    if 'items' in data and len(data['items']) > 0:
        video_item = data['items'][0]
        video_id = video_item['id']['videoId']
        video_title = video_item['snippet']['title']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        return Response(f'{video_title}: {video_url}', mimetype='text/plain')
    else:
        return Response(
            f'No video found matching the title "{video_query}".',
            mimetype='text/plain'
        ), 404

if __name__ == '__main__':
    app.run(debug=True)
