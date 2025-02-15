app.layout = html.Div([
    html.H3("İsterler", style={"text-align": "center"}),

    # En kısa yol bul
    html.Div([
        html.H4("1. En kısa yol bul"),
        dcc.Input(id="shortest-path-start", type="text", placeholder="Başlangıç Yazar ID'si",
                  style={"margin-right": "10px"}),
        dcc.Input(id="shortest-path-end", type="text", placeholder="Bitiş Yazar ID'si",
                  style={"margin-bottom": "10px"}),
        html.Button("En kısa yol bul", id="btn-1", style={"margin-bottom": "10px"})
    ], style={"margin-bottom": "20px", "padding": "10px", "border": "1px solid #ccc", "border-radius": "5px"}),

    # İşbirliği kuyruğu oluştur
    html.Div([
        html.H4("2. İşbirliği kuyruğu oluştur"),
        dcc.Input(id="queue-author-id", type="text", placeholder="Yazar ID'si",
                  style={"margin-bottom": "10px"}),
        html.Button("İşbirliği kuyruğu oluştur", id="btn-2", style={"margin-bottom": "10px"})
    ], style={"margin-bottom": "20px", "padding": "10px", "border": "1px solid #ccc", "border-radius": "5px"}),

    # BST oluştur
    html.Div([
        html.H4("3. BST oluştur"),
        dcc.Input(id="bst-author-id", type="text", placeholder="Yazar ID'si",
                  style={"margin-bottom": "10px"}),
        html.Button("BST oluştur", id="btn-3", style={"margin-bottom": "10px"})
    ], style={"margin-bottom": "20px", "padding": "10px", "border": "1px solid #ccc", "border-radius": "5px"}),

    # Kısa yollar hesapla
    html.Div([
        html.H4("4. Kısa yollar hesapla"),
        dcc.Input(id="shortest-all-id", type="text", placeholder="Yazar ID'si",
                  style={"margin-bottom": "10px"}),
        html.Button("Kısa yollar hesapla", id="btn-4", style={"margin-bottom": "10px"})
    ], style={"margin-bottom": "20px", "padding": "10px", "border": "1px solid #ccc", "border-radius": "5px"}),

    # İşbirlikçi sayısını hesapla
    html.Div([
        html.H4("5. İşbirlikçi sayısını hesapla"),
        dcc.Input(id="coauthor-count-id", type="text", placeholder="Yazar ID'si",
                  style={"margin-bottom": "10px"}),
        html.Button("İşbirlikçi sayısını hesapla", id="btn-5", style={"margin-bottom": "10px"})
    ], style={"margin-bottom": "20px", "padding": "10px", "border": "1px solid #ccc", "border-radius": "5px"}),

    # En çok işbirliği yapan yazar
    html.Div([
        html.H4("6. En çok işbirliği yapan yazar"),
        html.Button("En çok işbirliği yapan yazar", id="btn-6", style={"margin-bottom": "10px"})
    ], style={"margin-bottom": "20px", "padding": "10px", "border": "1px solid #ccc", "border-radius": "5px"}),

    # En uzun yol hesapla
    html.Div([
        html.H4("7. En uzun yol hesapla"),
        dcc.Input(id="longest-path-id", type="text", placeholder="Yazar ID'si",
                  style={"margin-bottom": "10px"}),
        html.Button("En uzun yol hesapla", id="btn-7", style={"margin-bottom": "10px"})
    ], style={"margin-bottom": "20px", "padding": "10px", "border": "1px solid #ccc", "border-radius": "5px"}),

    # İşlem Çıktıları
    html.Div(id="outputs", style={"padding": "10px", "background-color": "#f5f5f5", "margin-top": "20px"})
])
