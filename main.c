#include <stdio.h>
#include <stdlib.h>

#import "tokenizer/tokenize.c"

typedef struct Alphabet {
    char* rus_lower;
    char* rus_higher;

    char* eng_lower;
    char* eng_higher;

    char* punct;
    char* number;
} Alphabet;

/*
 * Vars
 */

int hash_size = 10000;

node* random_token(dictionary* hash_dictionary) {
    if (hash_dictionary == NULL) {
        fprintf(stderr, "Error: Empty dictionary\n");
        return NULL;
    }

    srand(_rdtsc());

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

void generate(Alphabet* alphabet, dictionary *hash_dictionary, FILE *output, int count) {
    node* prev = random_token(hash_dictionary);
    node* curr;
    if (prev == NULL) {
        return;
    }
    fputs(prev->data, output);

    int repeats = 0;
    for (; count > 0; count--) {
        // fputc(' ', output);
        if (prev->transition_count == 0) {
            generate(alphabet, hash_dictionary, output, count);
            return;
        }
        int next = rand() % prev->frequency_sum;

        for (int j = 0; j < prev->transition_count; j++) {
            if (next <= prev->frequencies[j]) {
                if (strchr(alphabet->punct, prev->transitions[j]->data[0]) == NULL) {
                    fputc(' ', output);
                }
                curr = prev->transitions[j];
                if (prev == curr) {
                    repeats++;
                    if (repeats >= 3) {
                        curr = random_token(hash_dictionary);
                        repeats = 0;

                        fputs(curr->data, output);
                        prev = curr;
                        break;
                    }
                }
                fputs(curr->data, output);
                prev = curr;
                break;
            }

            next -= prev->frequencies[j];
        }

int main(void) {
    Alphabet alphabet = {
        "àáâãäå¸æçèéêëìíîïğñòóôõö÷øùúûüışÿ",
        "ÀÁÂÃÄÅ¨ÆÇÈÉÊËÌÍÎÏĞÑÒÓÔÕÖ×ØÙÚÛÜİŞß",
        "abcdefghijklmnopqrstuvwxyz",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        ",.\"\'*:;%-+=!?(){}[]`~",
        "0123456789"
    };

    printf("Hello, World!\n");
    return 0;
}