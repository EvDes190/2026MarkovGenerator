#include <stdlib.h>
#include <string.h>

#import "linked_list.c"

typedef struct Hash_Dictionary {
    List** buckets;
    int size;
} dictionary;

/*
 * functions for work with Hash table
 */
int hash(char *token);
node* get_token(char *token, dictionary* dictionary);
int put_token(char *token, dictionary *dictionary);
dictionary* init(int size);
void free_dictionary(dictionary* dictionary);

int hash(char *token) {
    unsigned long long len = strlen(token);

    char pair[2] = {token[0]};
    if (len < 2) {
        pair[1] = '0';
    }

    for (int i = 2; i < len; i++) {
        pair[i % 2] ^= token[i % 2];
    }
    int result = pair[0] * pair[1];

    return result;
}

node* get_token(char *token, dictionary* dictionary) {
    int index = hash(token) % dictionary->size;
    return find_node(token, dictionary->buckets[index]);
}

int put_token(char *token, dictionary *dictionary) {
    int index = hash(token) % dictionary->size;
    if (find_node(token, dictionary->buckets[index]) == NULL) {
        fprintf(stderr, "Token %s is already in hash table", token);
        return -1;
    }

    if (append(token, dictionary->buckets[index]) != 0) {
        return index;
    }

    dictionary->buckets[index] = init_list();

    return append(token, dictionary->buckets[index]);
}

dictionary* init(int size) {
    dictionary* dict = (dictionary*) malloc(sizeof(dictionary));
    dict->size = size;
    dict->buckets = calloc(size, sizeof(List*));

    return dict;
}

void free_dictionary(dictionary* dictionary) {
    for (int i = 0; i < dictionary->size; i++) {
        free_list(dictionary->buckets[i]);
    }
    free(dictionary->buckets);
    free(dictionary);
}