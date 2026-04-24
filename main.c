#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <time.h>
#include <dirent.h>

#import "text.c"
#import "hash_table/hash_dictionary.c"


/*
 * Vars
 */

char* gen_path = "output/";
char* tok_path = "output/tokenized/";
char* text_path = "input/";
char* extension = ".txt";
char* toked = "_tokenized";
char* gen = "output/generated.txt";
char* chain = "output/chain.txt";

int main() {
    setlocale(LC_ALL, "ru_RU.CP1251");

    int j = 0;

    // FILE *f = fopen("output/tokenized/sobache_serdtse_1251_tokenized.txt", "w");
    // printf("%p\n", f);
    // fclose(f);


    Alphabet* alphabet = init_alphabet();


    // while (alphabet->punct[j] != '\0') {
    //     printf("%d\n", alphabet->punct[j]);
    //     j++;
    // }
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
            printf("%s\n", name);
            cat(source_path, 3, text_path, name, extension);
            FILE *source = fopen(source_path, "rb");

            cat(tok, 4, tok_path, name, toked, extension);
                FILE *debug = fopen("debug.txt", "wb");
                // printf("%s %s\n", source_path, tok);
            FILE *tokenized = fopen(tok, "w+");
            tokenize(source, tokenized, alphabet);
            fclose(tokenized);
            tokenized = fopen(tok, "r+b");
            text_processing(tokenized, dictionary);
            printf("\n");

            fclose(tokenized);
            fclose(source);
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