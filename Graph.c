#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <limits.h>

#define MAX_NODES 100
#define INF 999999

// ---------------- Graph Structures ----------------
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

    // undirected graph
    Edge* revEdge = (Edge*)malloc(sizeof(Edge));
    revEdge->dest = src;
    revEdge->weight = weight;
    revEdge->next = g->list[dest].head;
    g->list[dest].head = revEdge;
}

// ---------------- Dijkstra Algorithm ----------------
void dijkstra(Graph* g, int start, int dist[], int prev[]) {
    bool visited[MAX_NODES] = {false};
    for(int i=0;i<g->numNodes;i++){
        dist[i]=INF;
        prev[i]=-1;
    }
    dist[start]=0;

    for(int i=0;i<g->numNodes-1;i++){
        int u=-1, min=INF;
        for(int j=0;j<g->numNodes;j++){
            if(!visited[j] && dist[j]<min){
                u=j;
                min=dist[j];
            }
        }
        if(u==-1) break;
        visited[u]=true;

        for(Edge* e=g->list[u].head; e!=NULL; e=e->next){
            if(!visited[e->dest] && dist[u]+e->weight<dist[e->dest]){
                dist[e->dest]=dist[u]+e->weight;
                prev[e->dest]=u;
            }
        }
    }
}

// ---------------- Truck Structure ----------------
typedef struct {
    int id;
    int capacity;
    int load;
    int currentNode;
    int totalDistance;
} Truck;

// ---------------- Path Reconstruction ----------------
void reconstructPath(int prev[], int target, char* pathStr){
    int stack[MAX_NODES], top=-1, node=target;
    while(node!=-1){
        stack[++top]=node;
        node=prev[node];
    }
    for(int i=top;i>=0;i--){
        char buf[10];
        sprintf(buf,"%d",stack[i]);
        strcat(pathStr,buf);
        if(i>0) strcat(pathStr," -> ");
    }
}

// ---------------- Assign Truck to Next Bin ----------------
int assignTruckToBin(Graph* g, Truck* t, int bin, FILE* json){
    int dist[MAX_NODES], prev[MAX_NODES];
    dijkstra(g,t->currentNode,dist,prev);

    if(t->load < t->capacity){
        printf("\n[+] Truck %d moving to Bin %d (Distance: %d)\n",t->id,bin,dist[bin]);
        t->totalDistance += dist[bin];
        t->currentNode = bin;
        t->load++;

        // Export JSON
        char pathStr[512]="";
        reconstructPath(prev,bin,pathStr);
        fprintf(json,"  {\n    \"truck_id\": %d,\n    \"target_bin\": %d,\n    \"distance\": %d,\n    \"path\": \"%s\"\n  },\n",
            t->id,bin,dist[bin],pathStr);
        return 1;
    } else {
        printf("\n[!] Truck %d is full! Send to depot.\n",t->id);
        return -1;
    }
}

// ---------------- Return to Depot ----------------
void returnToDepot(Graph* g, Truck* t, int depotNode, FILE* json){
    int dist[MAX_NODES], prev[MAX_NODES];
    dijkstra(g,t->currentNode,dist,prev);

    printf("\n[↩] Truck %d returning to Depot (Distance: %d)\n",t->id,dist[depotNode]);
    t->totalDistance += dist[depotNode];
    t->currentNode = depotNode;
    t->load = 0;

    char pathStr[512]="";
    reconstructPath(prev,depotNode,pathStr);
    fprintf(json,"  {\n    \"truck_id\": %d,\n    \"target_bin\": %d,\n    \"distance\": %d,\n    \"path\": \"%s\"\n  },\n",
        t->id,depotNode,dist[depotNode],pathStr);
}

// ---------------- Main Simulation ----------------
int main(){
    Graph g;
    initGraph(&g,6);

    // Example city map
    addEdge(&g,0,1,4);
    addEdge(&g,0,2,2);
    addEdge(&g,1,2,1);
    addEdge(&g,1,3,5);
    addEdge(&g,2,3,8);
    addEdge(&g,3,4,3);
    addEdge(&g,4,5,2);

    Truck t1 = {1,3,0,0,0};

    int binsByPriority[100]; // simulate teammate module input
    int nBins=3;
    binsByPriority[0]=3;
    binsByPriority[1]=4;
    binsByPriority[2]=2;

    bool collected[MAX_NODES]={false};

    FILE* json=fopen("route_output.json","w");
    fprintf(json,"{\n\"routes\":[\n");

    int nextBinIndex=0;
    while(nextBinIndex<nBins){
        int currentBin=binsByPriority[nextBinIndex];

        if(collected[currentBin]){
            nextBinIndex++;
            continue;
        }

        int res=assignTruckToBin(&g,&t1,currentBin,json);
        if(res==-1){
            returnToDepot(&g,&t1,0,json);
            continue; // retry same bin after depot
        }

        // Simulate driver input
        printf("\nDriver action: 1=Truck Full, 2=Bin Picked: ");
        int driverAction;
        scanf("%d",&driverAction);

        if(driverAction==1){
            returnToDepot(&g,&t1,0,json);
        } else if(driverAction==2){
            collected[currentBin]=true;
            printf("[√] Bin %d marked as collected by driver\n",currentBin);
            nextBinIndex++;
        } else {
            printf("Invalid input. Try again.\n");
        }
    }

    // Final depot return
    if(t1.currentNode!=0) returnToDepot(&g,&t1,0,json);

    fprintf(json, "],\n\"total_distance\": %d\n}\n", t1.totalDistance);
    fclose(json);

    printf("\n✅ Simulation complete. Total distance: %d\n",t1.totalDistance);
    printf("📁 Routes exported to 'route_output.json'\n");

    return 0;
}
