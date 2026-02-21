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


int main(void) {
    Alphabet alphabet = {
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
        "abcdefghijklmnopqrstuvwxyz",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        ",.\"\'*:;%-+=!?(){}[]`~",
        "0123456789"
    };

    printf("Hello, World!\n");
    return 0;
}