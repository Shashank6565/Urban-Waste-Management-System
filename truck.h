#ifndef TRUCK_H
#define TRUCK_H

#include "bin.h"

// Truck structure
typedef struct {
    int id;
    int capacity;       // Max bins truck can carry at once
    int load;           // Current bins collected
} Truck;

// Truck operations
void init_truck(Truck* truck, int id, int capacity);
void collect_bins(Truck* truck, int max_bins);
void reset_truck_load(Truck* truck);

#endif
