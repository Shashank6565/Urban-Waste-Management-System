#include <stdio.h>
#include "priority.h"

// -----------------------------------------------------
//  GLOBAL HEAP INSTANCE
// -----------------------------------------------------
PriorityQueue heap;

// -----------------------------------------------------
//  Helper Functions (swap, compare, etc.)
// -----------------------------------------------------
static void swap_nodes(HeapNode* a, HeapNode* b) {
    HeapNode temp = *a;
    *a = *b;
    *b = temp;
}

// Priority is based on fill level percentage
static int get_bin_priority(Bin* bin) {
    return (bin->current_fill * 100) / bin->capacity;
}

// -----------------------------------------------------
//  HEAP INITIALIZATION
// -----------------------------------------------------
void init_heap() {
    heap.size = 0;
}

// -----------------------------------------------------
//  CHECK IF EMPTY
// -----------------------------------------------------
int is_empty() {
    return heap.size == 0;
}

// -----------------------------------------------------
//  INSERT BIN INTO HEAP
// -----------------------------------------------------
void push_bin_priority(Bin* bin) {
    if (heap.size >= MAX_BINS) {
        printf("Heap overflow! Cannot add bin %d\n", bin->id);
        return;
    }

    int priority = get_bin_priority(bin);
    heap.nodes[heap.size].bin = bin;
    heap.nodes[heap.size].priority = priority;
    int i = heap.size;
    heap.size++;

    // Up-heap (bubble up)
    while (i > 0) {
        int parent = (i - 1) / 2;
        if (heap.nodes[i].priority > heap.nodes[parent].priority) {
            swap_nodes(&heap.nodes[i], &heap.nodes[parent]);
            i = parent;
        } else break;
    }
}

// -----------------------------------------------------
//  REMOVE AND RETURN HIGHEST PRIORITY BIN
// -----------------------------------------------------
Bin* pop_highest_priority_bin() {
    if (is_empty()) {
        printf("Heap is empty, no bins to collect.\n");
        return NULL;
    }

    Bin* highest = heap.nodes[0].bin;
    heap.nodes[0] = heap.nodes[heap.size - 1];
    heap.size--;

    // Down-heap (heapify)
    int i = 0;
    while (1) {
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        int largest = i;

        if (left < heap.size && heap.nodes[left].priority > heap.nodes[largest].priority)
            largest = left;
        if (right < heap.size && heap.nodes[right].priority > heap.nodes[largest].priority)
            largest = right;

        if (largest != i) {
            swap_nodes(&heap.nodes[i], &heap.nodes[largest]);
            i = largest;
        } else break;
    }

    return highest;
}

// -----------------------------------------------------
//  UPDATE PRIORITY OF EXISTING BIN
// -----------------------------------------------------
void update_bin_priority(Bin* bin) {
    for (int i = 0; i < heap.size; i++) {
        if (heap.nodes[i].bin->id == bin->id) {
            heap.nodes[i].priority = get_bin_priority(bin);

            // Re-heapify up
            int j = i;
            while (j > 0) {
                int parent = (j - 1) / 2;
                if (heap.nodes[j].priority > heap.nodes[parent].priority) {
                    swap_nodes(&heap.nodes[j], &heap.nodes[parent]);
                    j = parent;
                } else break;
            }
            return;
        }
    }

    // If bin not found, insert it
    push_bin_priority(bin);
}

// -----------------------------------------------------
//  REMOVE BIN FROM HEAP
// -----------------------------------------------------
void remove_bin_from_heap(Bin* bin) {
    int i;
    for (i = 0; i < heap.size; i++) {
        if (heap.nodes[i].bin == bin) {
            break;
        }
    }

    if (i == heap.size) return;  // bin not found

    // Swap with last element
    heap.nodes[i] = heap.nodes[heap.size - 1];
    heap.size--;

    // Re-heapify
    if (i < heap.size) {
        int parent = (i - 1) / 2;
        if (heap.nodes[i].priority > heap.nodes[parent].priority)
            while (i > 0 && heap.nodes[i].priority > heap.nodes[parent].priority) {
                swap_nodes(&heap.nodes[i], &heap.nodes[parent]);
                i = parent;
                parent = (i - 1) / 2;
            }
        else
            // Down-heap if smaller than children
            while (1) {
                int left = 2 * i + 1;
                int right = 2 * i + 2;
                int largest = i;

                if (left < heap.size && heap.nodes[left].priority > heap.nodes[largest].priority)
                    largest = left;
                if (right < heap.size && heap.nodes[right].priority > heap.nodes[largest].priority)
                    largest = right;

                if (largest != i) {
                    swap_nodes(&heap.nodes[i], &heap.nodes[largest]);
                    i = largest;
                } else break;
            }
    }
}

// -----------------------------------------------------
//  PRINT HEAP STATE (for debugging)
// -----------------------------------------------------
void print_heap() {
    printf("\nCurrent Heap (size=%d):\n", heap.size);
    if (is_empty()) {
        printf("Heap is empty, no bins to collect.\n");
        return;
    }
    for (int i = 0; i < heap.size; i++) {
        printf("  Bin %d -> %d%% filled\n",
               heap.nodes[i].bin->id,
               heap.nodes[i].priority);
    }
}
