#include <stdio.h>
#include "bin.h"
#include "priority.h"
#include "random.h"
#include "truck.h"
#include "graph.h"

int main() {
    setup_random();
    init_heap();

    // ---------------- Graph setup ----------------
    Graph g;
    initGraph(&g, 6);
    addEdge(&g, 0, 1, 4);
    addEdge(&g, 0, 2, 2);
    addEdge(&g, 1, 2, 1);
    addEdge(&g, 1, 3, 5);
    addEdge(&g, 2, 3, 8);
    addEdge(&g, 3, 4, 3);
    addEdge(&g, 4, 5, 2);

    // ---------------- Bins ----------------
    Bin b1, b2, b3, b4, b5, b6, b7, b8;
    create_bin(&b1, 1, 100, "Sector 1");
    create_bin(&b2, 2, 100, "Sector 2");
    create_bin(&b3, 3, 100, "Sector 3");
    create_bin(&b4, 4, 100, "Sector 4");
    create_bin(&b5, 5, 100, "Sector 5");
    create_bin(&b6, 6, 100, "Sector 6");
    create_bin(&b7, 7, 100, "Sector 7");
    create_bin(&b8, 8, 100, "Sector 8");

    // ---------------- Truck ----------------
    Truck t1;
    init_truck(&t1, 1, 3);

    int choice, steps;

    do {
        printf("\n========== Garbage Collection System ==========\n");
        printf("1. View all bins\n");
        printf("2. Update bin fills\n");
        printf("3. View heap (priority queue)\n");
        printf("4. Collect bins using truck\n");
        printf("5. Reset truck load\n");
        printf("6. Simulate one step (update + collect + reset)\n");
        printf("7. Show shortest path (truck -> bin)\n");
        printf("0. Exit\n");
        printf("----------------------------------------------\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
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
                print_heap();
                break;

            case 4:
                collect_bins(&t1, 2);
                break;

            case 5:
                reset_truck_load(&t1);
                printf("Truck load reset.\n");
                break;

            case 6:
                printf("Enter steps to simulate: ");
                scanf("%d", &steps);
                for (int i = 0; i < steps; i++) {
                    printf("\n--- Step %d ---\n", i + 1);
                    update_bin_fill(&b1);
                    update_bin_fill(&b2);
                    update_bin_fill(&b3);
                    update_bin_fill(&b4);
                    update_bin_fill(&b5);
                    update_bin_fill(&b6);
                    update_bin_fill(&b7);
                    update_bin_fill(&b8);
                    print_heap();
                    collect_bins(&t1, 2);
                    reset_truck_load(&t1);
                }
                break;

            case 7: {
                int start, end;
                printf("Enter current truck node (0-8): ");
                scanf("%d", &start);
                printf("Enter bin node (0-8): ");
                scanf("%d", &end);
                printShortestPath(&g, start, end);
                break;
            }

            case 0:
                printf("\nExiting program. Goodbye!\n");
                break;

            default:
                printf("\nInvalid choice!\n");
        }
    } while (choice != 0);

    return 0;
}
