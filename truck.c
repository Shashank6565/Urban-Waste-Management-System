#include <stdio.h>
#include "truck.h"
#include "priority.h"
#include "bin.h"

// Initialize truck
void init_truck(Truck* truck, int id, int capacity) {
    truck->id = id;
    truck->capacity = capacity;
    truck->load = 0;
}

// Collect bins from the heap (up to max_bins)
void collect_bins(Truck* truck, int max_bins) {
    for (int i = 0; i < max_bins; i++) {
        Bin* bin = pop_highest_priority_bin();
        if (bin == NULL) break;  // Heap empty

        printf("Truck %d collecting Bin %d (fill: %d%%)\n",
               truck->id, bin->id, (bin->current_fill * 100) / bin->capacity);

        // Empty the bin
        reset_bin(bin);
        truck->load++;

        printf("Bin %d has been emptied.\n", bin->id);
    }
}

// Reset truck load after returning to depot
void reset_truck_load(Truck* truck) {
    truck->load = 0;
}
