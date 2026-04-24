from flask import Flask, jsonify, request
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# COLOQUE SUA CHAVE AQUI (cadastre-se em https://newsapi.org/register)
API_KEY = "a658ee666bd848f0aac76b772b781337"

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Buscador de Notícias</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; color: white; margin-bottom: 40px; }
            h1 { font-size: 2.5rem; margin-bottom: 10px; }
            .search-box {
                background: white;
                border-radius: 50px;
                padding: 5px;
                display: flex;
                gap: 10px;
                margin-bottom: 30px;
            }
            input {
                flex: 1;
                padding: 15px 25px;
                border: none;
                outline: none;
                font-size: 1.1rem;
                border-radius: 50px;
            }
            button {
                padding: 15px 40px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 50px;
                font-size: 1.1rem;
                cursor: pointer;
            }
            button:hover { background: #764ba2; }
            .loading { text-align: center; color: white; font-size: 1.2rem; margin: 40px; }
            .results-info { background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
            .articles-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 25px;
            }
            .article-card {
                background: white;
                border-radius: 15px;
                overflow: hidden;
                cursor: pointer;
                transition: transform 0.3s;
            }
            .article-card:hover { transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            .article-image { width: 100%; height: 200px; object-fit: cover; }
            .article-content { padding: 20px; }
            .article-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; color: #333; }
            .article-description { color: #666; font-size: 0.9rem; margin-bottom: 15px; }
            .article-meta { font-size: 0.8rem; color: #999; margin-bottom: 15px; }
            .read-more {
                display: inline-block;
                padding: 8px 20px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 20px;
                font-size: 0.9rem;
            }
            .error { background: #f44336; color: white; padding: 15px; border-radius: 10px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📰 Buscador de Notícias</h1>
                <p>Digite um termo para buscar as últimas notícias</p>
            </div>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Ex: Apple, Tecnologia, Futebol..." 
                       onkeypress="if(event.key === 'Enter') searchNews()">
                <button onclick="searchNews()">🔍 Buscar</button>
            </div>
            <div id="results"></div>
        </div>
        <script>
            async function searchNews() {
                const query = document.getElementById('searchInput').value.trim();
                if (!query) { alert('Digite um termo para buscar'); return; }
                
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '<div class="loading">🔍 Buscando notícias...</div>';
                
                try {
                    // CHAMA O BACKEND (Flask) - NÃO chama a NewsAPI diretamente!
                    const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    
                    if (data.error) {
                        resultsDiv.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                        return;
                    }
                    
                    if (data.total === 0) {
                        resultsDiv.innerHTML = '<div class="loading">😕 Nenhuma notícia encontrada</div>';
                        return;
                    }
                    
                    let html = `<div class="results-info">📊 ${data.total} notícias encontradas</div>`;
                    html += '<div class="articles-grid">';
                    
                    data.articles.forEach(article => {
                        const imageUrl = article.urlToImage || 'https://via.placeholder.com/400x200?text=Sem+Imagem';
                        const date = new Date(article.publishedAt).toLocaleString('pt-BR');
                        html += `
                            <div class="article-card" onclick="window.open('${article.url}', '_blank')">
                                <img class="article-image" src="${imageUrl}" onerror="this.src='https://via.placeholder.com/400x200?text=Imagem+Indisponível'">
                                <div class="article-content">
                                    <div class="article-title">${escapeHtml(article.title || 'Sem título')}</div>
                                    <div class="article-description">${escapeHtml((article.description || 'Sem descrição').substring(0, 200))}...</div>
                                    <div class="article-meta">📰 ${escapeHtml(article.source.name)} | 📅 ${date}</div>
                                    <span class="read-more">Ler artigo →</span>
                                </div>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    resultsDiv.innerHTML = html;
                    
                } catch (error) {
                    resultsDiv.innerHTML = `<div class="error">❌ Erro: ${error.message}</div>`;
                }
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        </script>
    </body>
    </html>
    """

@app.route('/search')
def search():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Digite um termo para buscar'}), 400
        
        # Data de 30 dias atrás (limite da API gratuita)
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
        
        # Requisição é feita do SERVIDOR, não do navegador!
        response = requests.get('https://newsapi.org/v2/everything', params=params)
        data = response.json()
        
        if data.get('status') == 'ok':
            return jsonify({'total': data['totalResults'], 'articles': data['articles']})
        else:
            return jsonify({'error': data.get('message', 'Erro na API')}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)