#include <stdio.h>
#include "bin.h"
#include "priority.h"
#include "random.h"
#include "truck.h"

int main() {
    setup_random();    // initialize RNG
    init_heap();       // initialize heap

    // Create bins
    Bin b1, b2, b3;
    create_bin(&b1, 1, 100, "Sector 1");
    create_bin(&b2, 2, 100, "Sector 2");
    create_bin(&b3, 3, 100, "Sector 3");

    // Create truck
    Truck t1;
    init_truck(&t1, 1, 3);   // truck can carry 3 bins at a time

    // Simulation loop: fill bins and collect
    for (int step = 0; step < 20; step++) {
        printf("\n--- Step %d ---\n", step+1);

        // Fill bins
        update_bin_fill(&b1);
        update_bin_fill(&b2);
        update_bin_fill(&b3);

        print_bin_status(&b1);
        print_bin_status(&b2);
        print_bin_status(&b3);

        // Print heap
        print_heap();

        // Truck collects up to 2 bins per step
        collect_bins(&t1, 2);

        // Reset truck after collection
        reset_truck_load(&t1);
    }

    return 0;
}
