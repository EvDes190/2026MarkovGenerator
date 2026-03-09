#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

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
    alphabet->punct = ",.\n\t:;!?–";
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

    fputs(buffer, output);

    clock_t end = clock();
    printf("tokenize: %lf seconds\n", (double) (end - begin) / CLOCKS_PER_SEC);
    return 0;
}

void text_processing(struct Hash_Dictionary *hash_dictionary, FILE *input) {
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