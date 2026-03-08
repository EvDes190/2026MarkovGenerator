#include <stdio.h>
#include <string.h>
#include <stdlib.h>

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

    // alphabet = {
    //     .rus_lower = malloc(33 * sizeof(char)),
    //     .rus_higher = malloc(33 * sizeof(char)),
    //     .eng_lower = "abcdefghijklmnopqrstuvwxyz",
    //     .eng_higher= "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    //     .punct = ",.\n\t:;!?",
    //     .special = "\"\'*%-+=(){}[]`~ ",
    //     .number = "0123456789"
    // };
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
    alphabet->punct = ",.\n\t:;!?";
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


        if (strchr(alphabet->rus_lower, symbol) != NULL || strchr(alphabet->eng_lower, symbol) != NULL) {

            // printf("%c", symbol);
            // fprintf(output, "-");
        } else if ((char_point = strchr(alphabet->rus_higher, symbol)) != NULL) {
            // fprintf(output, "-");
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
    return 0;
}