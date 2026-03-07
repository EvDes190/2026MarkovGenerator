#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
int append(const char *element, List *list);
void free_list(List *list);
node* find_node(const char* element, const List *list);
int pop(List *list, const char *element);
List* init_list();
int add_transition(node* current_token, node *transition_token);

/*
 * functions for work with transitions- rising massive
 */
int note_token(node* current_token, node *transition_token);

int append(const char *element, List *list) {
    if (list == NULL) {
        fprintf(stderr, "Error: List pointer is NULL\n");
        return 0;
    }
    node *newNode = malloc(sizeof(node));
    if (newNode == NULL) {
        fprintf(stderr, "Error: Memory allocation failed for node\n");
        return 0;
    }
    newNode->data = malloc((strlen(element) + 1) * sizeof(char));
    if (newNode->data == NULL) {
        fprintf(stderr, "Error: Memory allocation failed for node data\n");
    }

    strcpy(newNode->data, element);
    newNode->next = NULL;
    newNode->transitions = NULL;
    newNode->frequency_sum = 0;
    newNode->transition_count = 0;

    list->tail->next = newNode;
    list->tail = newNode;
    list->length++;

    return 1;
}

void free_list(List *list) {
    if (list == NULL) {
        // fprintf(stderr, "Error: List pointer is NULL for free.\n");
        return;
    }
    node *curr = list->head;
    while (curr != NULL) {
        node *temp = curr->next;
        free(curr->transitions);
        free(curr->frequencies);
        free(curr);
        curr = temp;
    }
    free(list);
}

node* find_node(const char* element, const List *list) {
    if (list == NULL || list->head == NULL) {
        fprintf(stderr, "Error: List is empty!\n");
        return NULL;
    }
    node *curr = list->head;
    while (curr != NULL) {
        if (strcmp(element, curr->data) == 0) {
            return curr;
        }
        curr = curr->next;
    }
    return NULL;
}

int pop(List *list, const char *element) {
    if (list == NULL || list->head == NULL) {
        fprintf(stderr, "Error: List is empty!\n");
        return -1;
    }

    list->length--;

    node *before = list->head;
    if (strcmp(element, before->data) == 0) {
        list->head = list->head->next;
        free(before);
        return 1;
    }
    node *curr = before->next;
    while (curr != NULL) {
        if (strcmp(element, curr->data) == 0) {
            before->next = curr->next;
            free(curr);
            return 1;
        }
    }

    return 0;
}

List* init_list() {
    List* list = malloc(sizeof(List));
    if (list == NULL) {
        fprintf(stderr, "Error: Memory allocation failed for list\n");
        return NULL;
    }
    list->head = NULL;
    list->tail = NULL;
    list->length = 0;
    return list;
}

int note_token(node* current_token, node *transition_token) {
    if (current_token == NULL) {
        fprintf(stderr, "Error: Token's node pointer is NULL!\n");
        return 0;
    }
    if (transition_token == NULL) {
        fprintf(stderr, "Error: Pointer to char is empty!\n");
        return 0;
    }

    int index = 0;
    if (current_token->transitions == NULL) {
        current_token->transitions = malloc(sizeof(node*));
        if (current_token->transitions == NULL) {
            fprintf(stderr, "Error: Memory allocation failed for transitions of \"%s\" token.", current_token->data);
            return -1;
        }
        current_token->frequencies = calloc(1, sizeof(int));
        if (current_token->frequencies == NULL) {
            fprintf(stderr, "Error: Memory allocation failed for frequencies of transition of \"%s\" token.", current_token->data);
            return -1;
        }
        current_token->transition_count = 1;
    } else {
        for (; index < current_token->transition_count; index++) {
            if (strcmp(current_token->transitions[index]->data, transition_token->data) == 0) {
                current_token->frequency_sum++;
                current_token->frequencies[index]++;


                // swap if left frequency lower than right
                if (index > 0) {
                    if (current_token->frequencies[index] > current_token->frequencies[index - 1]) {
                        int temp_freq = current_token->frequencies[index - 1];
                        current_token->frequencies[index - 1] = current_token->frequencies[index];
                        current_token->frequencies[index] = temp_freq;

                        node* temp_trans = current_token->transitions[index];
                        current_token->transitions[index] = current_token->transitions[index - 1];
                        current_token->transitions[index - 1] = temp_trans;
                    }
                }
                return 0;
            }
        }

        node** new_transitions = realloc(current_token->transitions, (current_token->transition_count + 1) * sizeof(node*));
        if (new_transitions == NULL) {
            fprintf(stderr, "Error: Memory allocation failed for transitions of \"%s\" token.", current_token->data);
        }
        int* new_frequencies = realloc(current_token->frequencies, (current_token->transition_count + 1) * sizeof(int));
        if (new_frequencies == NULL) {
            fprintf(stderr, "Error: Memory allocation failed for frequencies of transition of \"%s\" token.", current_token->data);
        }

        current_token->transitions = new_transitions;
        current_token->frequencies = new_frequencies;
        current_token->transition_count++;
    }

    current_token->frequency_sum++;
    current_token->transitions[index] = transition_token;
    current_token->frequencies[index]++;

    return 1;
}

int add_transition(node* current_token, node *transition_token) {
    if (current_token == NULL) {
        fprintf(stderr, "Error: Token's node pointer is NULL!\n");
        return -1;
    }
    if (transition_token == NULL) {
        fprintf(stderr, "Error: Pointer to char is empty!\n");
        return -1;
    }

    for (int index = 0; index < current_token->transition_count; index++) {
        if (strcmp(current_token->transitions[index]->data, transition_token->data) == 0) {
            current_token->frequency_sum++;
            current_token->frequencies[index]++;
            return index;
        }
    }

    node **new_transitions = realloc(current_token->transitions, (current_token->transition_count + 1) * sizeof(node*));
    int* new_frequencies = realloc(current_token->frequencies, (current_token->transition_count + 1) * sizeof(int));
    if (new_transitions != NULL && new_frequencies != NULL) {
        new_transitions[current_token->transition_count] = transition_token;
        new_frequencies[current_token->transition_count] = 1;
        current_token->transition_count++;
        current_token->frequency_sum++;

        current_token->transitions = new_transitions;
        current_token->frequencies = new_frequencies;
    } else {
        fprintf(stderr, "Error: Memory allocation failed for transitions of \"%s\" token.", current_token->data);
        return -1;
    }

    return current_token->transition_count - 1;
}
