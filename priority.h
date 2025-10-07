#include "bin.h" 

#define MAX_BINS 100

typedef struct {
    Bin* bin;
    int priority;
} HeapNode;

typedef struct {
    HeapNode nodes[MAX_BINS];
    int size;
} PriorityQueue;

// global
extern PriorityQueue heap;

void init_heap();
int is_empty();
void push_bin_priority(Bin* bin);
Bin* pop_highest_priority_bin();
void update_bin_priority(Bin* bin);
void print_heap();         
void remove_bin_from_heap(Bin* bin);