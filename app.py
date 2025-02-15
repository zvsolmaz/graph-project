from dash import Dash, html, dcc, Input, Output, State, dash
import dash_cytoscape as cyto
from dash import callback_context  # Import doğru olmalı
import pandas as pd
from graph import Graph, BST
import pandas as pd


def create_graph_from_excel(file_path):
    """
    Excel dosyasından veriyi okuyarak bir Graph nesnesi oluşturur.
    """
    # Veriyi yükle
    df = pd.read_excel(file_path)

    # Graph nesnesi oluştur
    graph = Graph()

    # Yazar-makale ilişkisini takip etmek için sözlük
    author_papers = {}

    for _, row in df.iterrows():
        # Ana yazar bilgileri
        main_author_name = graph.normalize_name(row['author_name'])
        main_author_orcid = row['orcid'] if pd.notna(row['orcid']) else f"author_{hash(main_author_name)}"
        paper_title = row['paper_title'].strip() if pd.notna(row['paper_title']) else "Makale bilgisi eksik"
        coauthors = eval(row['coauthors']) if pd.notna(row['coauthors']) else []

        # Ana yazarı grafa ekle
        if main_author_orcid not in graph.author_ids:
            graph.add_node(main_author_orcid, label=main_author_name)
        if main_author_name not in author_papers:
            author_papers[main_author_name] = []
        author_papers[main_author_name].append(paper_title)

        # Ortak makalelere dayalı kenarlar ekle
        for coauthor in coauthors:
            coauthor_name = graph.normalize_name(coauthor)
            coauthor_id = f"coauthor_{hash(coauthor_name)}"

            if coauthor_id not in graph.author_ids:
                graph.add_node(coauthor_id, label=coauthor_name)

            # Ortak makaleye dayalı kenarı ekle
            graph.add_edge(main_author_orcid, coauthor_id, label=paper_title)

            # Yardımcı yazarın makalelerini ilişkilendir
            if coauthor_name not in author_papers:
                author_papers[coauthor_name] = []
            author_papers[coauthor_name].append(paper_title)

    return graph, author_papers


def generate_elements(graph):
    """
    Grafın elemanlarını (düğümler ve kenarlar) oluşturur.
    """
    # Makale sayısını hesaplayın
    paper_counts = {node: len(graph.author_papers.get(node, [])) for node in graph.nodes}

    # Ortalama makale sayısını hesaplayın
    average_count = sum(paper_counts.values()) / len(paper_counts) if paper_counts else 0
    threshold_high = average_count * 1.2
    threshold_low = average_count * 0.8

    elements = []

    # Düğümler için stil belirleme
    for node in graph.nodes:
        paper_count = paper_counts.get(node, 0)

        # Düğüm boyut ve renk ayarları
        if paper_count > threshold_high:
            size = 90  # Büyük düğüm
            color = "#4B0082"  # Koyu mor
        elif paper_count < threshold_low:
            size = 50  # Küçük düğüm
            color = "#BA55D3"  # Açık mor
        else:
            size = 70  # Orta boyut
            color = "#800080"  # Orta koyulukta mor

        # Düğüm elemanını oluşturma
        elements.append({
            'data': {
                'id': node,
                'label': node,
                'papers': graph.author_papers.get(node, [])
            },
            'style': {
                'background-color': color,
                'width': size,
                'height': size
            }
        })

    # Kenarları ekleme
    for source, targets in graph.edges.items():
        for target, weight in targets.items():
            elements.append({
                'data': {
                    'source': source,
                    'target': target,
                    'weight': weight
                }
            })

    return elements

# Veri seti yolunu belirleyin
file_path = "C:\\Users\\zeynep\\Downloads\\PROLAB 3 - GÜNCEL DATASET.xlsx"

# Graph nesnesi oluşturuluyor
graph = Graph()

# Veri setini işleyerek graf oluşturuluyor
data = pd.read_excel(file_path)
for _, row in data.iterrows():
    # Coauthors listesini temizle
    coauthors = eval(row["coauthors"]) if isinstance(row["coauthors"], str) else []

    # Ana yazar ve makale bilgisi
    main_author = graph.normalize_name(row["author_name"])

    paper_title = row["paper_title"]

    # Ana yazarı ve makaleyi ekle
    graph.add_author_with_papers(main_author, [paper_title])

    # Coauthors ile bağlantılar oluştur
    for coauthor in coauthors:
        coauthor = graph.normalize_name(coauthor)
        graph.add_edge(main_author, coauthor)

# Grafın içeriğini kontrol et
graph.display_graph()

# Grafikten elemanları (nodes ve edges) oluştur
elements = generate_elements(graph)

# Dash Uygulaması
app = Dash(__name__)
app.title = "Yazarlar Grafı"


def dijkstra_shortest_path(graph, start, end):
    start = start.lower().strip()
    end = end.lower().strip()

    if start not in graph.nodes or end not in graph.nodes:
        return None, "Belirtilen yazar(lar) graf içinde bulunamadı."

    distances = {node: float('inf') for node in graph.nodes}
    previous_nodes = {node: None for node in graph.nodes}
    distances[start] = 0
    nodes = list(graph.nodes)

    while nodes:
        current_node = min(nodes, key=lambda node: distances[node])
        nodes.remove(current_node)

        if distances[current_node] == float('inf'):
            break

        for neighbor, weight in graph.edges[current_node].items():
            alternative_route = distances[current_node] + weight
            if alternative_route < distances[neighbor]:
                distances[neighbor] = alternative_route
                previous_nodes[neighbor] = current_node

    path, current = [], end
    while previous_nodes[current] is not None:
        path.insert(0, current)
        current = previous_nodes[current]

    if path:
        path.insert(0, current)

    return path, distances[end]


def update_graph_with_path(graph, path):
    """
    Yolu vurgulamak için Cytoscape elemanlarını günceller.
    """
    updated_elements = []
    for node in graph.nodes:
        updated_elements.append({
            'data': {
                'id': node,
                'label': node,
            },
            'classes': 'highlight' if node in path else ''
        })

    for source, targets in graph.edges.items():
        for target, weight in targets.items():
            updated_elements.append({
                'data': {
                    'source': source,
                    'target': target,
                    'weight': weight
                },
                'classes': 'highlight' if source in path and target in path else ''
            })

    return updated_elements


# def build_priority_queue(graph, author):
#     """
#     Bir yazarın işbirliği yaptığı yazarları düğüm ağırlıklarına göre sırala.
#     Ağırlık: Makale sayısı (author_papers).
#     """
#     if author not in graph.nodes:
#         return None, "Yazar graf içinde bulunamadı."
#
#     priority_queue = []
#     # İşbirliği yaptığı yazarları al
#     for coauthor in graph.edges.get(author, {}):
#         weight = len(graph.author_papers.get(coauthor, []))  # Makale sayısı
#         priority_queue.append((weight, coauthor))
#
#     # Kuyruğu ağırlıklara göre sırala (azalan sırada)
#     priority_queue.sort(reverse=True, key=lambda x: x[0])
#     return priority_queue

def build_priority_queue_with_steps(graph, author):
    """
    Bir yazarın işbirliği yaptığı yazarları makale sayısına göre sıralar ve işlemleri adım adım gösterir.

    Args:
        graph (Graph): Graf nesnesi
        author (str): Yazar ID'si veya ismi

    Returns:
        list of str: Her adımın açıklamalarını içeren bir liste
    """
    steps = []
    author = graph.normalize_name(author)  # Yazar ismini normalize et

    if author not in graph.nodes:
        return ["Belirtilen yazar graf içinde bulunamadı."]

    # İşbirliği yapılan yazarları bul
    priority_queue = []
    for coauthor in graph.edges.get(author, {}):
        weight = len(graph.author_papers.get(coauthor, []))  # Makale sayısı
        priority_queue.append((weight, coauthor))

    # Kuyruğa ekleme işlemlerini adım adım göster
    steps.append("Kuyruk başlatıldı.")
    for weight, coauthor in priority_queue:
        steps.append(f"Kuyruğa eklendi: {coauthor} (Makale sayısı: {weight})")

    # Kuyruğu ağırlıklara göre sırala
    priority_queue.sort(reverse=True, key=lambda x: x[0])
    steps.append("Kuyruk sıralandı.")

    # Kuyruktan çıkarma işlemlerini adım adım göster
    while priority_queue:
        top_item = priority_queue.pop(0)
        steps.append(f"Kuyruktan çıkarıldı: {top_item[1]} (Makale sayısı: {top_item[0]})")

    steps.append("Kuyruk işlemleri tamamlandı.")
    return steps


def visualize_bst(bst):
    """
    Binary Search Tree'yi Cytoscape elemanları olarak görselleştirir.
    :param bst: BST ağacı
    :return: Cytoscape elemanları (düğüm ve kenarlar)
    """
    elements = []

    def traverse(node, parent=None):
        if node:
            # Düğüm ekle
            elements.append({
                'data': {'id': str(node.key), 'label': f"{node.value} ({node.key})"}
            })

            # Edge ekle (parent -> child)
            if parent:
                elements.append({
                    'data': {'source': str(parent.key), 'target': str(node.key)}
                })

            # Sol ve sağ alt ağacı dolaş
            traverse(node.left, node)
            traverse(node.right, node)

    traverse(bst.root)  # Ağacı kökten itibaren dolaş
    return elements


def calculate_shortest_paths(graph, start_author):
    """
    A yazarından başlayarak işbirlikçileri ve onların işbirlikçileri arasında
    alt graf oluşturur ve tüm düğümlere olan en kısa yolları hesaplar.
    """
    if start_author not in graph.nodes:
        return None, "Yazar graf içinde bulunamadı."

    # Alt graf oluştur (işbirlikçiler ve onların işbirlikçileri)
    subgraph_nodes = {start_author}
    for neighbor in graph.edges[start_author]:
        subgraph_nodes.add(neighbor)
        subgraph_nodes.update(graph.edges[neighbor].keys())

    subgraph_edges = {
        node: {neighbor: graph.edges[node][neighbor] for neighbor in graph.edges[node] if neighbor in subgraph_nodes}
        for node in subgraph_nodes
    }

    # Alt graf için en kısa yolları hesapla
    distances = {node: float('inf') for node in subgraph_nodes}
    distances[start_author] = 0
    previous_nodes = {node: None for node in subgraph_nodes}
    unvisited_nodes = list(subgraph_nodes)

    while unvisited_nodes:
        current_node = min(unvisited_nodes, key=lambda node: distances[node])
        unvisited_nodes.remove(current_node)

        if distances[current_node] == float('inf'):
            break

        for neighbor, weight in subgraph_edges[current_node].items():
            alternative_route = distances[current_node] + weight
            if alternative_route < distances[neighbor]:
                distances[neighbor] = alternative_route
                previous_nodes[neighbor] = current_node

    # Tüm düğümler için yolları ve mesafeleri bul
    shortest_paths = []
    for node, distance in distances.items():
        path = []
        current = node
        while previous_nodes[current] is not None:
            path.insert(0, current)
            current = previous_nodes[current]
        if path:
            path.insert(0, current)
        shortest_paths.append((node, path, distance))

    return shortest_paths

import networkx as nx
def generate_shortest_paths_table(shortest_paths):
    """
    En kısa yolları bir HTML tablo olarak döndürür.
    """
    table_rows = [
        html.Tr([html.Th("Hedef Yazar"), html.Th("Yol"), html.Th("Mesafe")])
    ]
    for node, path, distance in shortest_paths:
        table_rows.append(html.Tr([
            html.Td(node),
            html.Td(" -> ".join(path)),
            html.Td(distance)
        ]))
    return html.Table(table_rows, style={"width": "100%", "border": "1px solid black", "border-collapse": "collapse"})

def calculate_positions(graph):
    """
    Düğümlerin pozisyonlarını NetworkX kullanarak hesaplar.

    Args:
        graph (Graph): Kullanıcı tarafından tanımlanan Graph nesnesi.

    Returns:
        dict: Düğüm ID'leri ile (x, y) koordinatlarını içeren bir sözlük.
    """
    # NetworkX grafını oluştur
    nx_graph = nx.Graph()
    for node1, neighbors in graph.edges.items():
        for node2, weight in neighbors.items():
            nx_graph.add_edge(node1, node2, weight=weight)

    # Spring layout (daha düzenli bir görünüm için)
    positions = nx.spring_layout(nx_graph, scale=100, seed=42)
    return {node: (pos[0] * 100, pos[1] * 100) for node, pos in positions.items()}
def visualize_shortest_path_with_plotly(graph, path, go=None):
    positions = calculate_positions(graph)  # Yeni pozisyon hesaplama fonksiyonu

    edge_x = []
    edge_y = []

    # Kenarlar için koordinatlar
    for i in range(len(path) - 1):
        x0, y0 = positions[path[i]]
        x1, y1 = positions[path[i + 1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='blue'),
        mode='lines',
        hoverinfo='none'
    )

    node_x = []
    node_y = []
    node_text = []

    for node in path:
        x, y = positions[node]
        node_x.append(x)
        node_y.append(y)

        # Düğüm etiketleri
        node_text.append(f"{node} (ID: {graph.author_ids.get(node, 'Unknown')})")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        marker=dict(
            size=15,
            color='red',
            line_width=2
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig

# Kısa yolları hesaplama ve görselleştirme fonksiyonu
def calculate_and_display_shortest_paths(graph, start_author):
    """
    A yazarından başlayarak işbirlikçi yazarlar arasında tüm en kısa yolları hesaplar.

    Args:
        graph (Graph): Graf nesnesi
        start_author (str): Başlangıç yazarı (ID)

    Returns:
        tuple: Güncellenmiş elemanlar ve tablo formatındaki sonuç
    """
    if start_author not in graph.nodes:
        return "Lütfen geçerli bir yazar ID'si girin.", []

    # Tüm düğümler için en kısa yolları hesapla
    shortest_paths = calculate_shortest_paths(graph, start_author)

    if not shortest_paths:
        return "Kısa yollar hesaplanamadı.", []

    # Tablo oluştur
    table_rows = []
    for target_author, path, distance in shortest_paths:
        if path:  # Yol mevcutsa ekle
            table_rows.append(html.Tr([
                html.Td(target_author),
                html.Td(" -> ".join(path)),
                html.Td(distance)
            ]))

    # Grafiği güncelle
    updated_elements = update_graph_with_path(graph, [p[1] for p in shortest_paths if p[1]])

    return updated_elements, html.Table(
        [html.Tr([html.Th("Hedef Yazar"), html.Th("Yol"), html.Th("Mesafe")])] + table_rows,
        style={"width": "100%", "border": "1px solid black", "border-collapse": "collapse"}
    )

def assign_positions_with_networkx(graph):
    """
    NetworkX ile düğüm pozisyonlarını hesaplar.
    """
    G = nx.Graph()

    # Kenarları ekle
    for source, targets in graph.edges.items():
        for target, weight in targets.items():
            G.add_edge(source, target, weight=weight)

    # Yerleşim pozisyonları (spring layout)
    positions = nx.spring_layout(G, scale=1, seed=42)
    return positions

def count_coauthors(graph, author):
    """
    Belirtilen bir yazarın işbirlikçi sayısını döndürür.
    """
    author = graph.normalize_name(author)  # Yazar ismini normalize et
    if author not in graph.nodes:
        return 0  # Yazar graf içinde bulunamadıysa işbirliği yok
    return len(graph.edges.get(author, {}))  # Komşu düğüm sayısını döndür



def find_most_collaborative_author(graph):
    max_collaborations = 0
    most_collaborative_author = None

    # Tüm düğümleri dolaş ve işbirliği sayısını kontrol et
    for author in graph.nodes:
        num_collaborations = len(graph.edges.get(author, {}))  # Komşuların sayısı
        if num_collaborations > max_collaborations:
            max_collaborations = num_collaborations
            most_collaborative_author = author

    return most_collaborative_author, max_collaborations


def find_longest_path(graph, start_author):
    """
    Bir yazar ID'sinden başlayarak graf içinde gidebileceği en uzun yolu bulur.

    Args:
        graph (Graph): Graf nesnesi
        start_author (str): Başlangıç yazarı (düğüm)

    Returns:
        tuple: En uzun yol (düğümler listesi) ve yol uzunluğu (düğüm sayısı)
    """
    if start_author not in graph.nodes:
        return None, "Yazar graf içinde bulunamadı."

    visited = set()
    longest_path = []
    max_length = 0

    def dfs(node, path):
        nonlocal longest_path, max_length
        visited.add(node)
        path.append(node)

        # Eğer mevcut yolun uzunluğu en uzunsa, güncelle
        if len(path) > max_length:
            max_length = len(path)
            longest_path = path[:]

        # Komşuları ziyaret et
        for neighbor in graph.edges.get(node, {}):
            if neighbor not in visited:
                dfs(neighbor, path)

        # Geri dönüş
        path.pop()
        visited.remove(node)

    # DFS'yi başlat
    dfs(start_author, [])

    return longest_path, max_length - 1  # Düğüm sayısı üzerinden uzunluk


def create_layout():
    return html.Div([
        # Sol Panel (Çıkışlar)
        html.Div(id="left-panel", children=[
            html.H3("İşlem Çıktıları", style={"text-align": "center"}),
            html.Div(id="outputs-main", style={
                "padding": "10px",
                "background-color": "#f5f5f5",
                "height": "90vh",
                "overflow-y": "scroll",
                "border": "1px solid #ccc"
            })
        ], style={
            "width": "20%",
            "display": "inline-block",
            "vertical-align": "top",
            "padding": "10px"
        }),

        # Orta Panel (Grafik Görselleştirme)
        html.Div(id="graph-container", children=[
            html.H3("Graf Görselleştirme", style={"text-align": "center"}),

            cyto.Cytoscape(
                id="cytoscape-graph",
                elements=generate_elements(graph),  # Düğüm ve kenar verileri
                stylesheet=[
                    {
                        'selector': 'node',
                        'style': {
                            'background-color': '#800080',  # Koyu mor
                            'width': 70,
                            'height': 70,
                            'label': 'data(label)',
                            'font-size': '14px',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'color': '#FFFFFF'  # Beyaz yazı rengi
                        }
                    },
                    {
                        'selector': 'edge',
                        'style': {
                            'line-color': '#ccc',  # Kenar rengi
                            'width': 2  # Kenar kalınlığı
                        }
                    },
                    {
                        'selector': 'node.highlight',
                        'style': {
                            'background-color': '#ff4500',  # Vurgulanan düğüm rengi
                            'border-width': 2,
                            'border-color': '#ff4500'
                        }
                    },
                    {
                        'selector': 'edge.highlight',
                        'style': {
                            'line-color': '#ff4500',  # Vurgulanan kenar rengi
                            'width': 4
                        }
                    }
                ],
                style={
                    'width': '100%',
                    'height': '70vh',
                    'border': '1px solid #ccc'
                },
                layout={'name': 'cose'}
            ),

            # Dinamik alt grafik (Butonlara göre değişir)
            html.Div(id="dynamic-graph-container", children=[
                cyto.Cytoscape(
                    id="cytoscape-graph-1",  # 1. buton için görselleştirme
                    elements=[],
                    style={
                        'width': '100%',
                        'height': '20vh',
                        'border': '1px solid #ccc',
                        'display': 'none'  # Başlangıçta gizli
                    },
                    layout={'name': 'cose'}
                ),
                cyto.Cytoscape(
                    id="cytoscape-graph-3",  # 3. buton için görselleştirme
                    elements=[],
                    style={
                        'width': '100%',
                        'height': '20vh',
                        'border': '1px solid #ccc',
                        'display': 'none'  # Başlangıçta gizli
                    },
                    layout={'name': 'cose'}
                ),
                cyto.Cytoscape(
                    id="cytoscape-graph-4",  # 4. buton için görselleştirme
                    elements=[],
                    style={
                        'width': '100%',
                        'height': '20vh',
                        'border': '1px solid #ccc',
                        'display': 'none'  # Başlangıçta gizli
                    },
                    layout={'name': 'cose'}
                )
            ])
        ], style={
            "width": "40%",
            "display": "inline-block",
            "padding": "10px"
        }),

        # Sağ Panel (İsterler ve Butonlar)
        html.Div(id="right-panel", children=[
            html.H3("İsterler", style={"text-align": "center"}),

            # 1. En kısa yol bul
            html.Div([
                html.H4("1. En kısa yol bul"),
                dcc.Input(id="shortest-path-start", type="text",
                          placeholder="Başlangıç Yazar ID'si", style={"margin-right": "10px"}),
                dcc.Input(id="shortest-path-end", type="text",
                          placeholder="Bitiş Yazar ID'si"),
                html.Button("En kısa yol bul", id="btn-1", style={"margin-top": "10px"}),
                html.Div(id="outputs1", style={"margin-top": "10px"})
            ], style={"margin-bottom": "20px"}),

            # 2. İşbirliği kuyruğu oluştur
            html.Div([
                html.H4("2. İşbirliği kuyruğu oluştur"),
                dcc.Input(id="queue-author-id", type="text",
                          placeholder="Yazar ID'si"),
                html.Button("Kuyruk oluştur", id="btn-2", style={"margin-top": "10px"}),
                html.Div(id="outputs2", style={"margin-top": "10px"})
            ], style={"margin-bottom": "20px"}),

            # 3. BST oluştur ve görselleştir
            html.Div([
                html.H4("3. BST oluştur"),
                dcc.Input(id="bst-author-id", type="text",
                          placeholder="Yazar ID'si"),
                html.Button("BST oluştur", id="btn-3", style={"margin-top": "10px"}),
                html.Div(id="outputs3", style={"margin-top": "10px"})
            ], style={"margin-bottom": "20px"}),

            # 4. Kısa yollar hesapla
            html.Div([
                html.H4("4. Kısa yollar hesapla"),
                dcc.Input(id="shortest-all-id", type="text",
                          placeholder="Yazar ID'si"),
                html.Button("Kısa yollar hesapla", id="btn-4", style={"margin-top": "10px"}),
                html.Div(id="outputs4", style={"margin-top": "10px"})
            ], style={"margin-bottom": "20px"}),

            # 5. İşbirlikçi sayısını hesapla
            html.Div([
                html.H4("5. İşbirlikçi sayısını hesapla"),
                dcc.Input(id="coauthor-count-id", type="text",
                          placeholder="Yazar ID'si"),
                html.Button("İşbirlikçi sayısını hesapla", id="btn-5", style={"margin-top": "10px"}),
                html.Div(id="outputs5", style={"margin-top": "10px"})
            ], style={"margin-bottom": "20px"}),

            # 6. En çok işbirliği yapan yazar
            html.Div([
                html.H4("6. En çok işbirliği yapan yazar"),
                html.Button("En çok işbirliği yapan yazar", id="btn-6", style={"margin-top": "10px"}),
                html.Div(id="outputs6", style={"margin-top": "10px"})
            ], style={"margin-bottom": "20px"}),

            # 7. En uzun yol hesapla
            html.Div([
                html.H4("7. En uzun yol hesapla"),
                dcc.Input(id="longest-path-id", type="text",
                          placeholder="Yazar ID'si"),
                html.Button("En uzun yol hesapla", id="btn-7", style={"margin-top": "10px"}),
                html.Div(id="outputs7", style={"margin-top": "10px"})
            ], style={"margin-bottom": "20px"})
        ], style={
            "width": "35%",
            "display": "inline-block",
            "vertical-align": "top",
            "padding": "10px"
        })
    ])


@app.callback(
    Output('outputs-main', 'children'),  # Sol panelde düğüm bilgilerini ve buton işlevlerini göster
    [Input('cytoscape-graph', 'tapNode')] + [Input(f"btn-{i}", 'n_clicks') for i in range(1, 8)],
    [State('shortest-path-start', 'value'),
     State('shortest-path-end', 'value'),
     State('queue-author-id', 'value'),
     State('bst-author-id', 'value'),
     State('shortest-all-id', 'value'),
     State('coauthor-count-id', 'value'),
     State('longest-path-id', 'value')]
)
def combined_callback(tap_node, *args):
    ctx = callback_context
    if not ctx.triggered:
        return "Henüz bir işlem yapılmadı."  # Hiçbir olay tetiklenmediyse

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]  # Tetiklenen elemanı al

    # Eğer bir düğüme tıklanmışsa
    if triggered_id == 'cytoscape-graph':
        if tap_node:
            node_data = tap_node['data']
            node_id = node_data.get('id', 'Bilinmiyor')
            node_label = node_data.get('label', 'Bilinmiyor')
            papers = node_data.get('papers', [])
            paper_list = "<ul>" + "".join([f"<li>{paper}</li>" for paper in papers]) + "</ul>"
            return f"""
                <b>Yazar ID:</b> {node_id}<br>
                <b>Yazar İsmi:</b> {node_label}<br>
                <b>Makaleler:</b> {paper_list}
            """
        return "Bir düğüme tıklayın."

    # Eğer bir buton tıklanmışsa
    button_ids = [f"btn-{i}" for i in range(1, 8)]
    if triggered_id in button_ids:
        index = button_ids.index(triggered_id) + 1
        if index == 1:
            # İlk buton işlemi: En kısa yol
            start_author = args[0]
            end_author = args[1]
            if not start_author or not end_author:
                return "Lütfen başlangıç ve bitiş yazar ID'lerini girin."
            return f"En kısa yol bulundu: {start_author} -> {end_author}"
        elif index == 2:
            # İkinci buton işlemi: Kuyruk oluştur
            author_id = args[2]
            if not author_id:
                return "Lütfen bir yazar ID'si girin."
            return f"{author_id} için işbirliği kuyruğu oluşturuldu."
        elif index == 3:
            bst_author = args[3]
            return f"{bst_author} için BST işlemi tamamlandı."
        elif index == 4:
            shortest_all = args[4]
            return f"{shortest_all} için tüm kısa yollar hesaplandı."
        elif index == 5:
            coauthor_count = args[5]
            return f"{coauthor_count} yazarının işbirlikçi sayısı hesaplandı."
        elif index == 6:
            return "En çok işbirliği yapan yazar bulundu."
        elif index == 7:
            longest_path = args[6]
            return f"{longest_path} için en uzun yol hesaplandı."

    return "Beklenmeyen bir durum oluştu."

@app.callback(
    Output('cytoscape-graph', 'elements'),
    [Input('btn-1', 'n_clicks')]  # İsterlerden birine tıklanınca
)
def update_main_graph(n_clicks):
    if n_clicks is None:
        return []  # Tıklama olmamışsa boş döndür

    # Ana grafiği oluşturacak verileri getirin
    elements = generate_elements(graph)
    return elements



@app.callback(
    [Output('cytoscape-graph-1', 'elements'),
     Output('cytoscape-graph-1', 'style'),
     Output('outputs1', 'children')],
    [Input('btn-1', 'n_clicks')],
    [State('shortest-path-start', 'value'),
     State('shortest-path-end', 'value')]
)
def update_graph_for_shortest_path(n_clicks, start_author, end_author):
    if n_clicks is None or not start_author or not end_author:
        return [], {'display': 'none'}, "Lütfen başlangıç ve bitiş yazar ID'lerini girin."

    # En kısa yol hesaplama
    result = dijkstra_shortest_path(graph, start_author, end_author)
    if result[0] is None:
        return [], {'display': 'none'}, "Bağlantı yok."

    path, distance = result
    elements = update_graph_with_path(graph, path)
    path_str = " -> ".join(path)

    return elements, {'display': 'block'}, f"En kısa yol: {path_str}, Mesafe: {distance}"


# Dijkstra algoritması: Adımları kaydeden versiyon
def dijkstra_shortest_path_with_steps(graph, start, end):
    steps = []
    start = start.lower().strip()
    end = end.lower().strip()

    if start not in graph.nodes or end not in graph.nodes:
        return None, None, ["Belirtilen yazar(lar) graf içinde bulunamadı."]

    distances = {node: float('inf') for node in graph.nodes}
    previous_nodes = {node: None for node in graph.nodes}
    distances[start] = 0
    nodes = list(graph.nodes)
    queue = [(0, start)]  # Priority queue

    steps.append(f"Kuyruk başlatıldı: {queue}")

    while nodes:
        # Kuyruktaki en düşük mesafeli düğümü seç
        current_distance, current_node = min(queue, key=lambda x: x[0])
        queue = [item for item in queue if item[1] != current_node]  # Kuyruktan çıkar
        nodes.remove(current_node)

        steps.append(f"Düğüm ziyaret ediliyor: {current_node}, Mesafe: {current_distance}")

        if distances[current_node] == float('inf'):
            break

        for neighbor, weight in graph.edges.get(current_node, {}).items():
            alternative_route = distances[current_node] + weight
            if alternative_route < distances[neighbor]:
                distances[neighbor] = alternative_route
                previous_nodes[neighbor] = current_node
                queue.append((alternative_route, neighbor))
                steps.append(f"Kuyruğa eklendi: {neighbor}, Mesafe: {alternative_route}")

    # Yol oluşturma
    path, current = [], end
    while previous_nodes[current] is not None:
        path.insert(0, current)
        current = previous_nodes[current]

    if path:
        path.insert(0, current)

    return path, distances[end], steps

def update_graph_with_path(graph, path):
    elements = []
    for node in graph.nodes:
        elements.append({
            'data': {
                'id': node,
                'label': node,
            },
            'classes': 'highlight' if node in path else ''
        })

    for source, targets in graph.edges.items():
        for target, weight in targets.items():
            elements.append({
                'data': {
                    'source': source,
                    'target': target,
                    'weight': weight
                },
                'classes': 'highlight' if source in path and target in path else ''
            })

    return elements



@app.callback(
    Output("outputs2", "children"),  # Çıkışlar alanına yazdır
    [Input("btn-2", "n_clicks")],  # 2. butona tıklama
    [State("queue-author-id", "value")]  # Yazar ID'si
)
def show_priority_queue_steps(n_clicks, author_id):
    if not author_id:
        return "Lütfen bir yazar ID'si girin."

    steps = build_priority_queue_with_steps(graph, author_id)
    return html.Pre("\n".join(steps))  # Adımları metin olarak yazdır

@app.callback(
    [Output('cytoscape-graph-3', 'elements'),  # Görselleştirilen BST
     Output('cytoscape-graph-3', 'style'),     # Görselleştirme stili
     Output('outputs3', 'children')],         # Çıktı metni
    [Input('btn-3', 'n_clicks')],             # 3. butona tıklama
    [State('bst-author-id', 'value')]         # Yazar ID'si girişi
)
def update_graph_for_bst(n_clicks, author_id):
    if n_clicks is None or not author_id:
        return [], {'display': 'none'}, "Henüz bir işlem yapılmadı."

    # Belirtilen yazarın işbirlikçilerinden BST oluştur
    author_id = graph.normalize_name(author_id)  # Yazar ID'yi normalize et
    if author_id not in graph.nodes:
        return [], {'display': 'none'}, "Belirtilen yazar graf içinde bulunamadı."

    steps = []  # İşlemleri kaydetmek için bir liste

    # İşbirlikçileri kuyruktan al
    neighbors = [(weight, neighbor) for neighbor, weight in graph.edges[author_id].items()]
    steps.append(f"Yazarın işbirlikçileri alındı: {len(neighbors)} adet işbirlikçi bulundu.")

    # BST'yi oluştur
    bst = BST()
    for weight, neighbor in neighbors:
        bst.insert(weight, neighbor)
        steps.append(f"Ağaç düğümü eklendi: {neighbor} (Ağırlık: {weight})")

    # Kullanıcıdan gelen yazar ID'sini ağaca ekledikten sonra sil
    if neighbors:
        bst.delete(neighbors[0][0])  # Örneğin ilk düğümü siliyoruz
        steps.append(f"Yazar ağacından silindi: {neighbors[0][1]}")

    # Ağacı görselleştir
    bst_elements = visualize_bst(bst)
    steps.append("BST görselleştirme tamamlandı.")

    # Adımları birleştirerek döndür
    steps_output = html.Ul([html.Li(step) for step in steps])
    return bst_elements, {'display': 'block'}, steps_output


@app.callback(
    [Output('cytoscape-graph-4', 'elements'),
     Output('cytoscape-graph-4', 'style'),
     Output('outputs4', 'children')],
    [Input('btn-4', 'n_clicks')],
    [State('shortest-all-id', 'value')]
)
def update_shortest_paths_graph(n_clicks, start_author):
    if n_clicks is None or not start_author:
        return [], {'display': 'none'}, "Lütfen bir yazar ID'si girin."

    # Kısa yolları hesapla
    shortest_paths = calculate_shortest_paths(graph, start_author)
    if shortest_paths is None:
        return [], {'display': 'none'}, "Kısa yollar hesaplanamadı."

    # Grafiği güncelle
    updated_elements = update_graph_with_path(graph, [p[1] for p in shortest_paths if p[1]])

    # Tabloyu oluştur
    table = generate_shortest_paths_table(shortest_paths)

    return updated_elements, {'display': 'block'}, table


@app.callback(
    Output('outputs5', 'children'),  # İşbirlikçi sayısı çıktısı
    [Input('btn-5', 'n_clicks')],   # 5. buton tıklama
    [State('coauthor-count-id', 'value')]  # Kullanıcıdan yazar ID girişi
)
def calculate_coauthor_count(n_clicks, author_id):
    if n_clicks is None or not author_id:
        return "Lütfen bir yazar ID'si girin."

    # İşbirlikçi sayısını hesapla
    coauthor_count = count_coauthors(graph, author_id)

    # Sonucu döndür
    if coauthor_count == 0:
        return f"{author_id} için işbirliği yapılan yazar bulunamadı."
    return f"{author_id} yazarının işbirliği yaptığı toplam yazar sayısı: {coauthor_count}"


@app.callback(
    Output('outputs6', 'children'),
    [Input('btn-6', 'n_clicks')]  # Buton tıklaması
)
def find_and_display_most_collaborative_author(n_clicks):
    if not n_clicks:
        return "Lütfen butona tıklayın."

    # En çok işbirliği yapan yazarı bul
    most_collaborative_author, collaboration_count = find_most_collaborative_author(graph)

    # Sonucu döndür
    if most_collaborative_author is None:
        return "Graf içinde işbirliği yapan yazar bulunamadı."
    return f"En çok işbirliği yapan yazar: {most_collaborative_author} ({collaboration_count} işbirlikçi)"


@app.callback(
    Output('outputs7', 'children'),
    [Input('btn-7', 'n_clicks')],  # 7. butona tıklama
    [State('longest-path-id', 'value')]  # Başlangıç yazar ID'si
)
def calculate_and_display_longest_path(n_clicks, start_author):
    if not n_clicks:
        return "Lütfen butona tıklayın."

    if not start_author:
        return "Lütfen bir yazar ID'si girin."

    # En uzun yolu bul
    longest_path, length = find_longest_path(graph, graph.normalize_name(start_author))

    # Sonucu döndür
    if longest_path is None:
        return length  # Hata mesajını döndür (ör. "Yazar graf içinde bulunamadı.")
    return f"En uzun yol: {' -> '.join(longest_path)}, Uzunluk: {length}"




if __name__ == "__main__":
    app.layout = create_layout()
    app.run_server(debug=True)