cmake_minimum_required(VERSION 4.0)
project(MarkovGenerator C)

set(CMAKE_C_STANDARD 99)

add_executable(MarkovGenerator main.c
        text_parser/tokenize.c
        hash_table/hash_dictionary.c
        hash_table/linked_list.c
)
