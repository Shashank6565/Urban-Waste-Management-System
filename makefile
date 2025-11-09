# Simple Makefile for Urban Waste Management System

# Compiler
CC = gcc

# Source files
SRC = main3.c bin.c graph.c priority.c random.c truck.c

# Output file
OUT = waste_sim.exe

# Default rule
all:
	$(CC) $(SRC) -o $(OUT)

# Run the program
run:
	./$(OUT)

# Clean up compiled files
clean:
	rm -f $(OUT)
