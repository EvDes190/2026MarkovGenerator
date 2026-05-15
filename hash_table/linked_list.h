//
// Created by EvDes on 15.05.2026.
//

#ifndef MARKOVGENERATOR_LINKED_LIST_H
#define MARKOVGENERATOR_LINKED_LIST_H
#include <stddef.h>

typedef struct node {
    struct node* next;
    char* data;

    // transitions with frequency of occurrence for every token
    struct node** transitions;
    int* frequencies;
    // sum of all frequencies
    int frequency_sum;
    int transition_count;
} node;

typedef struct list {
    node *head;
    node *tail;
    size_t length;
} List;

/*
 * functions for work with Linked list
 */
node* append(const char *element, List *list);
void free_list(List *list);
node* new_node(const char *str);
node* find_node(const char* element, const List *list);
int pop(List *list, const char *element);
List* init_list();

int note_token(node* current_token, node *transition_token);

#endif //MARKOVGENERATOR_LINKED_LIST_H