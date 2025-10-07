// #include "bin.h"   // for Bin struct

// // ------------------------------
// //  MAX HEAP for urgent bins
// // ------------------------------
// #define MAX_BINS 100

// // Each heap node stores a pointer to an existing Bin
// typedef struct {
//     Bin* bin;         // reference to bin object
//     int priority;     // fill percentage (0–100)
// } HeapNode;

// // Priority Queue structure
// typedef struct {
//     HeapNode nodes[MAX_BINS];
//     int size;
// } PriorityQueue;

// // Global heap instance (can also be declared externally if needed)
// extern PriorityQueue heap;

// // ------------------------------
// //  Function Declarations
// // ------------------------------
// void init_heap();
// int  is_empty();
// void push_bin_priority(Bin* bin);
// Bin* pop_highest_priority_bin();
// void update_bin_priority(Bin* bin);
// void print_heap();           // for debugging

#include "bin.h"   // for Bin struct

#define MAX_BINS 100

typedef struct {
    Bin* bin;         // reference to bin object
    int priority;     // fill percentage (0–100)
} HeapNode;

typedef struct {
    HeapNode nodes[MAX_BINS];
    int size;
} PriorityQueue;

// Global heap instance
extern PriorityQueue heap;

// ------------------------------
// Function Declarations
// ------------------------------
void init_heap();
int is_empty();
void push_bin_priority(Bin* bin);
Bin* pop_highest_priority_bin();
void update_bin_priority(Bin* bin);
void print_heap();           // for debugging
void remove_bin_from_heap(Bin* bin);   // NEW function
