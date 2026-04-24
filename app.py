from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# COLOQUE SUA CHAVE AQUI (ou use a variável de ambiente)
API_KEY = "sua_chave_api_aqui"  # <-- SUBSTITUA PELA SUA CHAVE

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Termo não informado'}), 400
    
    # Data de 30 dias atrás
    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')
    
    params = {
        'q': query,
        'from': from_date,
        'to': to_date,
        'sortBy': 'publishedAt',
        'apiKey': API_KEY,
        'pageSize': 30,
        'language': 'pt'
    }
    
    try:
        response = requests.get('https://newsapi.org/v2/everything', params=params)
        data = response.json()
        
        if data.get('status') == 'ok':
            return jsonify({'total': data['totalResults'], 'articles': data['articles']})
        else:
            return jsonify({'error': data.get('message', 'Erro na API')}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)