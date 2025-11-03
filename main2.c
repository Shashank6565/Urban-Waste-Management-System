#include <stdio.h>
#include "bin.h"
#include "priority.h"
#include "random.h"
#include "truck.h"

int main() {
    setup_random();      // Initialize random number generator
    init_heap();         // Initialize priority heap
    int steps=0;
    // Create bins
    Bin b1, b2, b3,b4,b5,b6,b7,b8;
    create_bin(&b1, 1, 100, "Sector 1");
    create_bin(&b2, 2, 100, "Sector 2");
    create_bin(&b3, 3, 100, "Sector 3");
    create_bin(&b4, 4, 100, "Sector 4");
    create_bin(&b5, 5, 100, "Sector 5");
    create_bin(&b6, 6, 100, "Sector 6");
    create_bin(&b7, 7, 100, "Sector 7");
    create_bin(&b8, 8, 100, "Sector 8");

    // Create truck
    Truck t1;
    init_truck(&t1, 1, 3);

    int choice;

    do {
        printf("\n========== Garbage Collection System ==========\n");
        printf("1. View all bins\n");
        printf("2. Update bin fills\n");
        printf("3. View heap (priority queue)\n");
        printf("4. Collect bins using truck\n");
        printf("5. Reset truck load\n");
        printf("6. Simulate steps (update + collect + reset)\n");
        printf("0. Exit\n");
        printf("----------------------------------------------\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                printf("\n--- Bin Status ---\n");
                print_bin_status(&b1);
                print_bin_status(&b2);
                print_bin_status(&b3);
                print_bin_status(&b4);
                print_bin_status(&b5);
                print_bin_status(&b6);
                print_bin_status(&b7);
                print_bin_status(&b8);
                break;

            case 2:
                printf("\n--- Updating Bin Fill Levels ---\n");
                update_bin_fill(&b1);
                update_bin_fill(&b2);
                update_bin_fill(&b3);
                update_bin_fill(&b4);
                update_bin_fill(&b5);
                update_bin_fill(&b6);
                update_bin_fill(&b7);
                update_bin_fill(&b8);
                printf("Bin fill levels updated.\n");
                break;

            case 3:
                printf("\n--- Heap / Priority Queue ---\n");
                print_heap();
                break;

            case 4:
                printf("\n--- Truck Collecting Bins ---\n");
                collect_bins(&t1, 2);   // collect 2 bins (adjust if needed)
                break;

            case 5:
                printf("\n--- Resetting Truck Load ---\n");
                reset_truck_load(&t1);
                printf("Truck load reset successfully.\n");
                break;

            case 6:
                // int steps; 
                printf("input no of steps to simulate \n");
                scanf("%d",&steps);
                for(int i=0;i<steps;i++)
                {
                printf("\n--- Step %d ---\n", i+1);
                // printf("\n--- Simulating One Step ---\n");
                update_bin_fill(&b1);
                update_bin_fill(&b2);
                update_bin_fill(&b3);
                update_bin_fill(&b4);
                update_bin_fill(&b5);
                update_bin_fill(&b6);
                update_bin_fill(&b7);
                update_bin_fill(&b8);

                print_bin_status(&b1);
                print_bin_status(&b2);
                print_bin_status(&b3);
                print_bin_status(&b4);
                print_bin_status(&b5);
                print_bin_status(&b6);
                print_bin_status(&b7);
                print_bin_status(&b8);
                print_heap();
                collect_bins(&t1, 2);
                reset_truck_load(&t1);
                }
                printf("Step simulation completed.\n");
                break;

            case 0:
                printf("\nExiting the program. Goodbye!\n");
                break;

            default:
                printf("\nInvalid choice! Please try again.\n");
        }

    } while (choice != 0);

    return 0;
}