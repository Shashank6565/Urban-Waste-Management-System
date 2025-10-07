#ifndef BIN_H
#define BIN_H

#define EMPTY 0
#define FILLING 1
#define URGENT 2
#define COLLECTED 3
#define URGENT_THRESHOLD 70

typedef struct
{
    int id,capacity,current_fill;
    char location[50];
    int status;
}Bin;

void create_bin(Bin* bin, int id, int cap, const char* location);


void update_bin_fill(Bin* bin);

void report_bin_full(Bin* bin);

void reset_bin(Bin* bin);

void print_bin_status(const Bin* bin);        //for debugging 


#endif