
# 🧠 Academic Collaboration Network Visualization – Dash + NetworkX + Pandas

This is an interactive data visualization project developed in Python using Dash, NetworkX, and Pandas. It processes an academic dataset of authors and publications to display a collaboration graph and enables operations such as shortest path detection and BFS traversal.

📁 **Project Type**: University Project – Programming Lab III  
🛠️ **Tech Stack**: Python, Dash, Plotly, NetworkX, Pandas  
📊 **Dataset**: Excel-based author-publication data (custom schema)  
📌 **Language**: 🇬🇧 English (UI), 🇹🇷 Turkish (Output Text)

---

## 🚀 Features

- 🔍 **Find Shortest Path** between two authors
- 🔁 **Breadth-First Traversal** starting from any author
- 📈 **Visualize** the entire co-authorship graph
- 🖱️ **Interactive UI** with Dash (input boxes, buttons, results)
- 📋 **Real-time Output** of graph algorithms
- 📤 Supports **large datasets**

---

## 🖼️ Sample Screenshot

![Graph UI](assets/screenshots/graph-ui-example.png)

---

## 🧠 How It Works

1. **Loads dataset**: Authors, co-authorships, articles
2. **Creates undirected graph** via NetworkX
3. **Visualizes graph** using Plotly’s Dash
4. **UI provides**:
   - Author input
   - Shortest path between two nodes
   - BFS queue generation from a source
5. **Outputs** collaboration paths, distances, and BFS steps

---

## 📁 Folder Structure

```bash
graph-project/
├── app.py                   # Main Dash app
├── data/
│   └── PROLAB 3 - GÜNCEL DATASET.xlsx
├── assets/
│   ├── styles.css
│   └── screenshots/
│       └── graph-ui-example.png
├── requirements.txt         # Required Python packages
└── README.md
```

---

## ⚙️ How to Run

1. Clone the repo:
```bash
git clone https://github.com/your-username/graph-project.git
cd graph-project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
python app.py
```

4. Open your browser and go to:
```
http://127.0.0.1:8050/
```

---

## 🔧 Dependencies

- `dash`
- `networkx`
- `pandas`
- `plotly`
- `openpyxl`

Make sure `requirements.txt` includes them.

---

## 🇹🇷 Türkçe Açıklama – Akademik İşbirliği Ağı Görselleştirme

Bu proje, bir akademik makale veri seti üzerinden yazarlar arasındaki işbirliklerini **graf yapısıyla** gösteren interaktif bir uygulamadır. Kullanıcı, iki yazar arasında en kısa yolu bulabilir veya bir yazar üzerinden işbirliği sırasını (BFS) görebilir.

### Özellikler

- 🧩 Yazarlar arası en kısa yol bulma (Graph Theory)
- 🔄 Genişlik öncelikli arama (Breadth-First Search)
- 🌐 Dinamik Dash arayüzü (input, butonlar, anlık çıktı)
- 📊 Tüm graf görselleştirme (Plotly ile etkileşimli)
- 📂 Excel dosyasından veri çekme

---

## 👨‍💻 Nasıl Kullanılır?

1. `PROLAB 3 - GÜNCEL DATASET.xlsx` dosyasını `data/` klasörüne koyun.
2. `app.py` dosyasını çalıştırın:
```bash
python app.py
```
3. Tarayıcınızda şu adrese gidin:
```
http://127.0.0.1:8050/
```

---

## 👥 Geliştiriciler

- 👩‍💻 Zeynep Vuslat Solmaz – Backend, Algoritmalar, Veri Hazırlama
- 👩‍💻 Rahime Uysal – UI Tasarımı, Grafiksel Arayüz, Dokümantasyon

---

## 📃 Ek Bilgi

- Kaynak dosya: `PROLAB 3 - GÜNCEL DATASET.xlsx`
- Kullanılan algoritmalar: BFS, Shortest Path (Dijkstra benzeri)
- Her düğüm (node) bir yazarı, her kenar (edge) bir işbirliğini temsil eder.
