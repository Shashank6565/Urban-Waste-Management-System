#include <stdlib.h>
#include <time.h>
#include "random.h"

void setup_random()
{
    srand(time(NULL));
}
int get_random_increment()
{
    return rand()%20 + 10;
}