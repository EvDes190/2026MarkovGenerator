//
// Created by EvDes on 15.05.2026.
//

#ifndef MARKOVGENERATOR_HASH_DICTIONARY_H
#define MARKOVGENERATOR_HASH_DICTIONARY_H

#include "linked_list.h"

typedef struct Hash_Dictionary {
    List** buckets;
    int size;
} dictionary;

unsigned int hash(char *token);
node* get_token(char *token, dictionary* dictionary);
node* put_token(char *token, dictionary *dictionary);
dictionary* init_dictionary(int size);
void free_dictionary(dictionary* dictionary);
node* random_token(dictionary* hash_dictionary, int seed);
void print_chain(dictionary *hash_dictionary, FILE* output);

#endif //MARKOVGENERATOR_HASH_DICTIONARY_H