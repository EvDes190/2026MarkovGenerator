cmake_minimum_required(VERSION 4.0)
project(MarkovGenerator C)

set(CMAKE_C_STANDARD 99)

add_executable(MarkovGenerator main.c
        hash_table/hash_dictionary.h
        hash_table/linked_list.h
        text.h

)
