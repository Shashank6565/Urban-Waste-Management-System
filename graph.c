#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "graph.h"

void initGraph(Graph* g, int n) {
    g->numNodes = n;
    for (int i = 0; i < n; i++)
        g->list[i].head = NULL;
}

void addEdge(Graph* g, int src, int dest, int weight) {
    Edge* newEdge = (Edge*)malloc(sizeof(Edge));
    newEdge->dest = dest;
    newEdge->weight = weight;
    newEdge->next = g->list[src].head;
    g->list[src].head = newEdge;

    // Undirected
    Edge* rev = (Edge*)malloc(sizeof(Edge));
    rev->dest = src;
    rev->weight = weight;
    rev->next = g->list[dest].head;
    g->list[dest].head = rev;
}

void dijkstra(Graph* g, int start, int dist[], int prev[]) {
    bool visited[MAX_NODES] = {false};
    for (int i = 0; i < g->numNodes; i++) {
        dist[i] = INF;
        prev[i] = -1;
    }
    dist[start] = 0;

    for (int i = 0; i < g->numNodes - 1; i++) {
        int u = -1, min = INF;
        for (int j = 0; j < g->numNodes; j++) {
            if (!visited[j] && dist[j] < min) {
                u = j;
                min = dist[j];
            }
        }
        if (u == -1) break;
        visited[u] = true;

        for (Edge* e = g->list[u].head; e != NULL; e = e->next) {
            if (!visited[e->dest] && dist[u] + e->weight < dist[e->dest]) {
                dist[e->dest] = dist[u] + e->weight;
                prev[e->dest] = u;
            }
        }
    }
}

void reconstructPath(int prev[], int target, char* pathStr) {
    int stack[MAX_NODES], top = -1, node = target;
    while (node != -1) {
        stack[++top] = node;
        node = prev[node];
    }
    for (int i = top; i >= 0; i--) {
        char buf[10];
        sprintf(buf, "%d", stack[i]);
        strcat(pathStr, buf);
        if (i > 0) strcat(pathStr, " -> ");
    }
}

void printShortestPath(Graph* g, int start, int end) {
    int dist[MAX_NODES], prev[MAX_NODES];
    dijkstra(g, start, dist, prev);

    char pathStr[256] = "";
    reconstructPath(prev, end, pathStr);

    printf("\n📍 Shortest path from %d to %d: %s (Distance: %d)\n",
           start, end, pathStr, dist[end]);
}
