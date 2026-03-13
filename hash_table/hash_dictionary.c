#include <stdlib.h>
#include <x86intrin.h>
#include <time.h>

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
node* random_token(dictionary* hash_dictionary, int seed);
void print_chain(dictionary *hash_dictionary, FILE* output);

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

node* random_token(dictionary* hash_dictionary, int seed) {
    if (hash_dictionary == NULL) {
        fprintf(stderr, "Error: Empty dictionary\n");
        return NULL;
    }

    srand(seed == 0 ? time(NULL) * clock() : seed);


    int first_bucket = rand() % hash_dictionary->size;
    int i = first_bucket;
    for (;i % hash_dictionary->size != first_bucket - 1;
        i++) {
        if (hash_dictionary->buckets[i % hash_dictionary->size] != NULL)
            break;
        }
    first_bucket = i % hash_dictionary->size;
    if (hash_dictionary->buckets[first_bucket] == NULL) {
        return NULL;
    }

    int first_node = rand() % hash_dictionary->buckets[first_bucket]->length;

    node* tok = hash_dictionary->buckets[first_bucket]->head;
    for (int j = 0; j < first_node; j++) {
        tok = tok->next;
    }

    // fputs(tok->data, stdout);
    return tok;
}

void print_chain(dictionary *hash_dictionary, FILE* output) {

    for (int i = 0; i < hash_dictionary->size; i++) {
        if (hash_dictionary->buckets[i] != NULL) {
            node *temp = hash_dictionary->buckets[i]->head;
            // fprintf(output, "\n==== %d ====\n\n", i);
            while (temp != NULL) {

                fprintf(output, ">%s<\n\t%d:\t", temp->data, temp->frequency_sum);
                int j = 0;

                while (temp->transition_count > j) {
                    fprintf(output, "\"%s\": %d, ", temp->transitions[j]->data, temp->frequencies[j]);
                    j++;
                }
                fprintf(output, "\n");
                temp = temp->next;
            }

        }
    }
}