#include <stdio.h>
#include <string.h>
#include "bin.h"
#include "random.h"
#include "priority.h"

void create_bin(Bin* bin, int id, int capacity, const char* location)
{
    bin->id=id;
    bin->capacity=capacity;
    bin->current_fill=0;
    strncpy(bin->location,location,sizeof(bin->location));
    bin->location[sizeof(bin->location)-1]='\0';
    bin->status=EMPTY;
}

void update_bin_fill(Bin* bin)
{
    int inc=get_random_increment();
    bin->current_fill+=inc;

    if(bin->current_fill>=bin->capacity)
    {
        bin->current_fill=bin->capacity;
        report_bin_full(bin);
    }
    else if ((bin->current_fill * 100) / bin->capacity >= URGENT_THRESHOLD)
    {
        bin->status=URGENT;
        report_bin_full(bin);
    }
    else if(bin->current_fill>0)
    {
        bin->status=FILLING;
    }
}

void report_bin_full(Bin* bin)
{
    bin->status=URGENT;
    update_bin_priority(bin);
}

void reset_bin(Bin* bin)
{
    bin->current_fill=0;
    bin->status=EMPTY;
    remove_bin_from_heap(bin);
}

void print_bin_status(const Bin* bin)
{
    const char* status_str[] = {"EMPTY", "FILLING", "URGENT", "COLLECTED"};
    printf("Bin %d [%s]: %d/%d filled (%s)\n",
           bin->id, bin->location,
           bin->current_fill, bin->capacity,
           status_str[bin->status]);
}