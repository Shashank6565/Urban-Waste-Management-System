#include <stdio.h>
#include "bin.h"
#include "priority.h"
#include "random.h"
#include "truck.h"

int main() {
    setup_random();    
    init_heap();       
    //  just simulated 3 bins 
    // badme aur add kardenge
    Bin b1, b2, b3,b4,b5;
    create_bin(&b1, 1, 100, "Sector 1");
    create_bin(&b2, 2, 100, "Sector 2");
    create_bin(&b3, 3, 100, "Sector 3");
    create_bin(&b4, 4, 100, "Sector 4");
    create_bin(&b5, 5, 100, "Sector 5");

    // Create truck
    Truck t1;
    init_truck(&t1, 1, 3);  

    
    for (int step = 0; step < 40; step++) {
        printf("\n--- Step %d ---\n", step+1);

       
        update_bin_fill(&b1);
        update_bin_fill(&b2);
        update_bin_fill(&b3);
        update_bin_fill(&b4);
        update_bin_fill(&b5);

        print_bin_status(&b1);
        print_bin_status(&b2);
        print_bin_status(&b3);
        print_bin_status(&b4);
        print_bin_status(&b5);

       
        print_heap();

       
        collect_bins(&t1, 4);

        
        reset_truck_load(&t1);
    }

    return 0;
}
