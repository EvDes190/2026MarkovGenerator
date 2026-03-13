#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <time.h>
#include <dir.h>
#include <io.h>
#include <dirent.h>

#import "text.c"
#import "hash_table/hash_dictionary.c"


/*
 * Vars
 */

char* gen_path = "output/";
char* tok_path = "output/tokenized/";
char* text_path = "assets/texts/bulgakov/";
char* extension = ".txt";
char* toked = "_tokenized";
char* gen = "output/generated.txt";
char* chain = "output/chain.txt";


int hash_size = 10000;

int main() {
    setlocale(LC_ALL, "ru_RU.CP1251");

    int j = 0;


    Alphabet* alphabet = init_alphabet();


    while (alphabet->punct[j] != '\0') {
        printf("%d\n", alphabet->punct[j]);
        j++;
    }
    dictionary* dictionary = init_dictionary(30000);

    DIR *dir = opendir(text_path);
    char name[260];
    char ext[40];
    struct dirent *entry;
    entry = readdir(dir);

    char *source_path = calloc(strlen(text_path) + strlen(extension) + 260, sizeof(char));
    char *tok = calloc(strlen(tok_path) + strlen(toked) + strlen(extension) + 260, sizeof(char));
    while (entry) {
        split_filename(name, ext, entry->d_name);

        if (strcmp(ext, extension) == 0) {
            cat(source_path, 3, text_path, name, extension);
            FILE *source = fopen(source_path, "rb");
            cat(tok, 4, tok_path, name, toked, extension);

            FILE *tokenized = fopen(tok, "rwb");
            tokenize(source, tokenized, alphabet);
            text_processing(tokenized, dictionary);

            memset(source, 0, (strlen(text_path) + strlen(extension) + 260) * sizeof(char));
            memset(tok, 0, (strlen(tok_path) + strlen(toked) + strlen(extension) + 260) * sizeof(char));
            memset(ext, 0, 40 * sizeof(char));
        }

        entry = readdir(dir);
    }
    closedir(dir);


    int seed = 0;
    FILE *out = fopen(gen, "w");
    generate(out, alphabet, dictionary, 100000, seed);

    FILE *debug = fopen(chain, "w");
    print_chain(dictionary, debug);

    clock_t end = clock();
    printf("total time: %lf seconds\n", (double) end / CLOCKS_PER_SEC);

    return 0;
}