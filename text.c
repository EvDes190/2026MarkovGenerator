#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdarg.h>

#import "hash_table/hash_dictionary.c"

typedef struct Alphabet {
    char* rus_lower;
    char* rus_higher;

    char* eng_lower;
    char* eng_higher;

    char* punct;
    char* special;
    char* number;
} Alphabet;

Alphabet* init_alphabet() {
    Alphabet* alphabet = malloc(sizeof(Alphabet));

    alphabet->rus_lower = malloc(33 * sizeof(char));
    alphabet->rus_higher = malloc(33 * sizeof(char));
    alphabet->eng_lower = malloc(27 * sizeof(char));
    alphabet->eng_higher = malloc(27 * sizeof(char));
    alphabet->punct = malloc(20 * sizeof(char));
    alphabet->special = malloc(20 * sizeof(char));
    alphabet->number = malloc(20 * sizeof(char));

    for (char i = 0; i < 32; i++) {
        alphabet->rus_lower[i] = i + 224;
        alphabet->rus_higher[i] = i + 192;
    }
    alphabet->rus_lower[32] = '\0';
    alphabet->rus_higher[32] = '\0';

    alphabet->eng_lower = "abcdefghijklmnopqrstuvwxyz";
    alphabet->eng_higher = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    char* punct = ",.\n\t:;!?";
    alphabet->punct[0] = 0b10010110; // –
    alphabet->punct[1] = 0b10100000; // NBSP
    alphabet->punct[2] = '\0';
    strcat(alphabet->punct, punct);
    alphabet->special = "\"\'*%-+=(){}[]`~ ";
    alphabet->number = "0123456789";

    return alphabet;
}

void free_alphabet(Alphabet* alphabet) {
    free(alphabet->rus_lower);
    free(alphabet->rus_higher);
    free(alphabet->eng_lower);
    free(alphabet->eng_higher);
    free(alphabet->punct);
    free(alphabet->special);
    free(alphabet->number);
    free(alphabet);
}

void cat(char* buf, int n, ...) {
    va_list strings;
    va_start(strings, n);
    strcpy(buf, va_arg(strings, char*));
    for (int i = 1; i < n; i++) {
        strcat(buf, va_arg(strings, char*));
    }
    va_end(strings);
}


void split_filename(char *name, char *ext, const char *source) {
    int len = strlen(source);

    while (source[--len] != '.' && len >= 0) {}
    strcpy(ext, source + len);
    memcpy(name, source, len + 1);
    name[len] = '\0';
}

int tokenize(FILE *input, FILE *output, Alphabet* alphabet) {
    clock_t begin = clock();

    char symbol;
    char buffer[1025];
    int buffer_top = -1;

    int token_reading = 0;

    char* char_point;
    long long char_index;


    while (fread(&symbol, sizeof(char), 1, input) != 0) {

        if (buffer_top > 512 & token_reading == 0 | buffer_top < 1024) {
            buffer[buffer_top + 1] = '\0';
            fputs(buffer, output);
            buffer_top = -1;
            memset(buffer, 0, sizeof(char) * 1024);
            token_reading = 0;
        }


        if (strchr(alphabet->rus_lower, symbol) != NULL || strchr(alphabet->eng_lower, symbol) != NULL || strchr(alphabet->number, symbol) != NULL) {

        } else if ((char_point = strchr(alphabet->rus_higher, symbol)) != NULL) {

            char_index = char_point - alphabet->rus_higher;
            symbol = alphabet->rus_lower[char_index];

        } else if ((char_point = strchr(alphabet->eng_higher, symbol)) != NULL) {
            char_index = char_point - alphabet->eng_higher;
            symbol = alphabet->eng_lower[char_index];

        } else {
            buffer[++buffer_top] = ' ';
            if (strchr(alphabet->punct, symbol) != NULL) {
                buffer[++buffer_top] = symbol;
                buffer[++buffer_top] = ' ';
            }
            token_reading = 0;
            continue;
        }

        if (token_reading == 0) {
            token_reading = 1;
        }
        buffer[++buffer_top] = symbol;

    }
    buffer[++buffer_top] = '\0';

    // fputs(buffer, output);

    clock_t end = clock();
    printf("tokenize: %lf seconds\n", (double) (end - begin) / CLOCKS_PER_SEC);
    return 0;
}

void text_processing(FILE *input, struct Hash_Dictionary *hash_dictionary) {
    clock_t begin = clock();

    char buffer[1000];
    char c;
    int buffer_top = -1;
    int token_reading = 0;

    node* prev = NULL;
    node* curr = NULL;

    while (fread(&c, 1, 1, input) != 0) {
        if (c == ' ') {
            if (token_reading == 1) {
                buffer[++buffer_top] = '\0';
                token_reading = 0;
                buffer_top = -1;

                prev = curr;
                curr = put_token(buffer, hash_dictionary);
                if (prev != NULL && curr != NULL) {
                    note_token(prev, curr);
                }
            }

        } else {
            buffer[++buffer_top] = c;
            if (token_reading == 0) {
                token_reading = 1;
            }
        }
    }
    clock_t end = clock();
    printf("processing: %lf seconds\n", (double) (end - begin) / CLOCKS_PER_SEC);
}

int is_punct(const Alphabet *alphabet, const char c) {
    int i = 0;
    while (alphabet->punct[i] != '\0') {
        if (alphabet->punct[i] == c) {
            return 1;
        }

        i++;
    }

    return 0;
}

int space_condition(const Alphabet* alphabet, node* prev, node* curr) {
    return is_punct(alphabet, curr->data[0]) == 0 || alphabet->punct[0] == curr->data[0];
}

void generate(FILE* output, const Alphabet* alphabet, dictionary *hash_dictionary, int count, int seed) {
    if (seed == 0) {
        srand(time(NULL));
    } else {
        srand(seed);
    }

    clock_t begin = clock();

    node* prev = random_token(hash_dictionary, seed);
    node* curr = NULL;
    if (prev == NULL) {
        return;
    }
    fputs(prev->data, output);

    int repeats = 0;
    for (; count > 0; count--) {
        if (prev->transition_count == 0) {
            prev = random_token(hash_dictionary, rand());
        }
        int next = rand() % prev->frequency_sum + 1;

        for (int j = 0; j < prev->transition_count; j++) {
            if (next <= prev->frequencies[j]) {
                // if (strchr(alphabet->punct, prev->transitions[j]->data[0]) == NULL) {
                //     fputc(' ', output);
                // }
                curr = prev->transitions[j];
                if (prev == curr) {
                    if (repeats >= 3) {
                        curr = random_token(hash_dictionary, rand());
                        repeats = 0;
                    }
                    repeats++;
                }

                if (space_condition(alphabet, prev, curr)) {
                    fputc(' ', output);
                }


                fputs(curr->data, output);
                prev = curr;
                break;
            }

            next -= prev->frequencies[j];
        }
    }

    clock_t end = clock();
    printf("generate: %lf seconds\n", (double) (end - begin) / CLOCKS_PER_SEC);
}