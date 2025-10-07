#include <stdlib.h>
#include <time.h>
#include "../include/random.h"

void setup_random()     //whoever makes simulation
{
    srand(time(NULL));
}
int get_random_increment()
{
    return rand()%10 + 1;
}