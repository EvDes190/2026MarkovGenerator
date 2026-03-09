#include <stdlib.h>

#import "linked_list.c"

typedef struct Hash_Dictionary {
    List** buckets;
    int size;
} dictionary;

/*
 * functions for work with Hash table
 */
unsigned int hash(char *token);
node* get_token(char *token, dictionary* dictionary);
node* put_token(char *token, dictionary *dictionary);
dictionary* init_dictionary(int size);
void free_dictionary(dictionary* dictionary);

unsigned int hash(char *token) {
    // using djb hash-function

    unsigned int result = 5381;
    int c;
    int i = 0;
    while ((c = token[i]) != '\0') {
        result = result * 33 + c;
        i++;
    }

    return result;
}

node* get_token(char *token, dictionary* dictionary) {
    int index = hash(token) % dictionary->size;
    return find_node(token, dictionary->buckets[index]);
}

node* put_token(char *token, dictionary *dictionary) {
    int index = hash(token) % dictionary->size;
    node* temp;
    if (dictionary->buckets[index] == NULL) {
        dictionary->buckets[index] = init_list();
    } else if ((temp = find_node(token, dictionary->buckets[index])) != NULL) {
        return temp;
    }

    return append(token, dictionary->buckets[index]);
}

dictionary* init_dictionary(int size) {
    dictionary* dict = malloc(sizeof(dictionary));
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