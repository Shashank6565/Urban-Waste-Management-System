// graph.h
#include <stdbool.h>

#define MAX_NODES 100
#define INF 9

typedef struct Edge {
    int dest;
    int weight;
    struct Edge* next;
} Edge;

typedef struct {
    Edge* head;
} AdjList;

typedef struct {
    AdjList list[MAX_NODES];
    int numNodes;
} Graph;

// Core functions
void initGraph(Graph* g, int n);
void addEdge(Graph* g, int src, int dest, int weight);
void dijkstra(Graph* g, int start, int dist[], int prev[]);
void reconstructPath(int prev[], int target, char* pathStr);
void printShortestPath(Graph* g, int start, int end);
