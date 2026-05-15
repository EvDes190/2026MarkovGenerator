//
// Created by EvDes on 15.05.2026.
//

#ifndef MARKOVGENERATOR_TEXT_H
#define MARKOVGENERATOR_TEXT_H

#include <stdio.h>
#include "hash_table/hash_dictionary.h"

typedef struct Alphabet {
    char* rus_lower;
    char* rus_higher;

    char* eng_lower;
    char* eng_higher;

    char* punct;
    char* special;
    char* number;
} Alphabet;

Alphabet* init_alphabet();
void free_alphabet(Alphabet* alphabet);
void cat(char* buf, int n, ...);
void split_filename(char *name, char *ext, const char *source);
int tokenize(FILE *input, FILE *output, Alphabet* alphabet);
void text_processing(FILE *input, struct Hash_Dictionary *hash_dictionary);
int is_punct(const Alphabet *alphabet, const char c);
int space_condition(const Alphabet* alphabet, node* prev, node* curr);
void generate(FILE* output, const Alphabet* alphabet, dictionary *hash_dictionary, int count, int seed);

#endif //MARKOVGENERATOR_TEXT_H