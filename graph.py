import ast

import networkx as nx
import numpy as np
import pandas as pd
import sys
sys.path.append(r"C:\Users\zeynep\PycharmProjects\PythonProject3")

class MinHeap:
    """Elle bir Min-Heap implementasyonu."""

    def _init_(self):
        self.heap = []

    def insert(self, item):
        """Heap'e bir eleman ekler ve düzenler."""
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def remove(self):
        """Heap'ten en küçük elemanı çıkarır ve döner."""
        if len(self.heap) == 0:
            raise IndexError("Heap boş.")
        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def _heapify_up(self, index):
        """Heap'in yukarıdan aşağıya düzenlenmesi."""
        parent_index = (index - 1) // 2
        if index > 0 and self.heap[index][0] < self.heap[parent_index][0]:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            self._heapify_up(parent_index)

    def _heapify_down(self, index):
        """Heap'in aşağıdan yukarıya düzenlenmesi."""
        smallest = index
        left_child = 2 * index + 1
        right_child = 2 * index + 2

        if left_child < len(self.heap) and self.heap[left_child][0] < self.heap[smallest][0]:
            smallest = left_child

        if right_child < len(self.heap) and self.heap[right_child][0] < self.heap[smallest][0]:
            smallest = right_child

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)

    def is_empty(self):
        """Heap'in boş olup olmadığını kontrol eder."""
        return len(self.heap) == 0


class Graph:
    def __init__(self):  # Düzeltildi: __init_ doğru yazılmış olmalı
        self.nodes = set()  # Tüm düğümler (ID veya isim)
        self.edges = {}  # Kenar bağlantıları
        self.author_papers = {}  # Yazarların makaleleri
        self.author_ids = {}  # Yazar ID eşleştirmesi
        self.id_counter = 1  # Yazar ID'leri için sayaç
        self.author_labels = {}  # Yazarın etiketleri
    def add_author_with_papers(self, author_name, papers):
        """
        Yazar ve makale bilgilerini graf yapısına ekler.
        """
        author_node = self.normalize_name(author_name)
        self.add_node(author_node)

        if author_node not in self.author_papers:
            self.author_papers[author_node] = []
        self.author_papers[author_node].extend(papers)  # Makale bilgilerini ekle

    def normalize_name(self, name):
        return name.strip().lower().replace("'", "").replace("[", "").replace("]", "")

    def add_node(self, identifier):
        """
        Düğüm ekler (ID veya normalize edilmiş isimlere göre).
        """
        if identifier not in self.nodes:
            self.nodes.add(identifier)
            self.edges[identifier] = {}

    def add_edge(self, node1, node2):
        """
        İki düğüm arasında kenar ekler. Eğer düğümler aynıysa bağlantıyı eklemez.
        """
        if node1 == node2:  # Kendiyle bağlantıyı engelle
            return

        self.add_node(node1)
        self.add_node(node2)

        if node2 not in self.edges[node1]:
            self.edges[node1][node2] = 1
        else:
            self.edges[node1][node2] += 1

        if node1 not in self.edges[node2]:
            self.edges[node2][node1] = 1
        else:
            self.edges[node2][node1] += 1

        if node1 != node2:  # Kendine bağlanmayı önler
            self.edges[node1][node2] = self.edges[node1].get(node2, 0) + 1
            self.edges[node2][node1] = self.edges[node2].get(node1, 0) + 1

    def calculate_node_categories(self):
        """
        Düğümleri makale sayılarına göre sınıflandırır ve boyut/renk özellikleri ekler.
        """
        paper_counts = {node: len(self.author_papers.get(node, [])) for node in self.nodes}
        avg_count = sum(paper_counts.values()) / len(paper_counts) if paper_counts else 0
        threshold = avg_count * 1.2  # %20 üzeri eşik

        node_categories = {}
        for node, count in paper_counts.items():
            if count >= threshold:
                node_categories[node] = {'size': 80, 'color': '#4B0082'}  # Büyük ve koyu renk
            else:
                node_categories[node] = {'size': 40, 'color': '#9370DB'}  # Küçük ve açık renk

        return node_categories
    def add_author_with_coauthors(self, author_id, author_name, coauthors):
        """
        Ana yazar ve yardımcı yazarlar arasındaki bağlantıları ekler.
        """
        author_node = author_id if author_id else self.normalize_name(author_name)  # Ana yazar ID'si varsa kullan

        # Ana yazarı düğüme ekle
        self.add_node(author_node)

        for coauthor_name in coauthors:
            coauthor_node = self.normalize_name(coauthor_name)
            self.add_edge(author_node, coauthor_node)

    def display_graph(self):
        """
        Grafın düğüm ve kenar yapısını gösterir.
        """
        for node, neighbors in self.edges.items():
            print(f"Node: {node} -> İşbirlikleri: {len(neighbors)}")

    def add_edges_from_authors(self, main_author, coauthors):
        main_author = self.normalize_name(main_author)
        self.add_node(main_author)

        for author in coauthors:
            author = self.normalize_name(author)
            if author:  # Boş isimleri atlıyoruz
                self.add_node(author)
                self.add_edge(main_author, author)

    def adjust_node_sizes(graph, base_size=10, scale_factor=3):
        sizes = {node: base_size + scale_factor * len(graph.edges[node]) for node in graph.nodes}
        return sizes

    def filter_graph(graph, min_collaborations=5):
        filtered_nodes = {node for node in graph.nodes if len(graph.edges[node]) >= min_collaborations}
        filtered_graph = Graph()

        for node1 in filtered_nodes:
            for node2, weight in graph.edges[node1].items():
                if node2 in filtered_nodes:
                    filtered_graph.add_edge(node1, node2)
        return filtered_graph



    def dijkstra(self, start, end):
        start = self.normalize_name(start)
        end = self.normalize_name(end)

        if start not in self.nodes or end not in self.nodes:
            return None, "Belirtilen yazar(lar) graf içinde bulunamadı."

        distances = {node: float('infinity') for node in self.nodes}
        distances[start] = 0
        previous_nodes = {node: None for node in self.nodes}
        priority_queue = MinHeap()

        priority_queue.insert((0, start))

        while not priority_queue.is_empty():
            current_distance, current_node = priority_queue.remove()

            if current_node == end:
                break

            for neighbor, weight in self.edges[current_node].items():
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    priority_queue.insert((distance, neighbor))

        path = []
        current = end
        while current is not None:
            path.insert(0, current)
            current = previous_nodes[current]

        if distances[end] == float('infinity'):
            return None, "Bağlantı yok"

        return path, distances[end]

class BSTNode:
    def __init__(self, key, value):
        """
        İkili Arama Ağacı Düğümü
        :param key: Sıralama için kullanılacak anahtar (örneğin işbirliği ağırlığı)
        :param value: Anahtar ile ilişkilendirilen veri (örneğin yazar adı)
        """
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        """
        İkili Arama Ağacı Başlangıç Yapısı
        """
        self.root = None

    def insert(self, key, value):
        """
        Ağaca yeni bir düğüm ekler.
        :param key: Sıralama için kullanılacak anahtar
        :param value: Anahtar ile ilişkilendirilen veri
        """
        self.root = self._insert_recursive(self.root, key, value)

    def _insert_recursive(self, node, key, value):
        """
        Rekürsif olarak ağaca düğüm ekler.
        :param node: Mevcut düğüm
        :param key: Yeni düğümün anahtarı
        :param value: Yeni düğümün değeri
        """
        if node is None:
            return BSTNode(key, value)
        if key < node.key:
            node.left = self._insert_recursive(node.left, key, value)
        elif key > node.key:
            node.right = self._insert_recursive(node.right, key, value)
        return node

    def inorder_traversal(self):
        """
        Ağacı sıralı olarak gezer.
        :return: (key, value) çiftlerinden oluşan bir liste
        """
        results = []
        self._inorder_recursive(self.root, results)
        return results

    def _inorder_recursive(self, node, results):
        """
        Rekürsif olarak sıralı geçiş yapar.
        :param node: Mevcut düğüm
        :param results: Sonuçları tutan liste
        """
        if node is not None:
            self._inorder_recursive(node.left, results)
            results.append((node.key, node.value))
            self._inorder_recursive(node.right, results)

    def search(self, key):
        """
        Ağacın içinde belirtilen anahtarı arar.
        :param key: Aranan anahtar
        :return: Bulunan düğümün değeri veya None
        """
        return self._search_recursive(self.root, key)

    def _search_recursive(self, node, key):
        """
        Rekürsif olarak ağacın içinde belirtilen anahtarı arar.
        :param node: Mevcut düğüm
        :param key: Aranan anahtar
        :return: Bulunan düğümün değeri veya None
        """
        if node is None:
            return None
        if key == node.key:
            return node.value
        elif key < node.key:
            return self._search_recursive(node.left, key)
        else:
            return self._search_recursive(node.right, key)

    def delete(self, key):
        """
        Ağacın içinden belirtilen anahtarı siler.
        :param key: Silinecek anahtar
        """
        self.root = self._delete_recursive(self.root, key)

    def _delete_recursive(self, node, key):
        """
        Rekürsif olarak belirtilen anahtarı siler.
        :param node: Mevcut düğüm
        :param key: Silinecek anahtar
        :return: Yeni düğüm yapısı
        """
        if node is None:
            return node
        if key < node.key:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.key:
            node.right = self._delete_recursive(node.right, key)
        else:
            # Düğüm bulundu
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            # İki çocuğu varsa
            min_larger_node = self._min_value_node(node.right)
            node.key = min_larger_node.key
            node.value = min_larger_node.value
            node.right = self._delete_recursive(node.right, min_larger_node.key)
        return node

    def _min_value_node(self, node):
        """
        Sağ alt ağacın minimum değerli düğümünü bulur.
        :param node: Sağ alt ağacın kökü
        :return: Minimum değerli düğüm
        """
        current = node
        while current.left is not None:
            current = current.left
        return current
