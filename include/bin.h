#ifndef BIN_H
#define BIN_H

#define EMPTY 0
#define FILLING 1
#define URGENT 2
#define COLLECTED 3
#define URGENT_THRESHOLD 70

typedef struct
{
    int ID,capacity,current_fill;
    char location[50];
    int status;
}Bin;

void create_bin(){}

void update_bin_fill(){}

void update_bin_fill(){}

void report_bin_bill(){}

void reset_bin(){}

void print_bin_status(){}



#endif