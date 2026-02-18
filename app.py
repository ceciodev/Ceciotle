<!DOCTYPE html>
<html>
<head>
    <title>Indovina l'Artista</title>
    </head>
<body>
    <div class="container">
        <h1>🎵 Indovina l'Artista</h1>
        
        <form method="POST">
            <select name="nome" required>
                <option value="" disabled selected>Scegli un artista...</option>
                {% for artista in artisti %}
                <option value="{{ artista.nome }}">{{ artista.nome }}</option>
                {% endfor %}
            </select>
            <button type="submit">Prova</button>
        </form>

        {% if feedback %}
        <div class="result">
            <p><strong>Nome:</strong> {{ feedback[0] }}</p>
            <p>{{ feedback[1] }}</p>
            <p>{{ feedback[2] }}</p>
            <p>{{ feedback[3] }}</p>
            <p>{{ feedback[4] }}</p>
            <p>{{ feedback[5] }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
