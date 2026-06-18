# sources/security-integrity/selinux/libsepol/cil/src/cil_list.c

## Purpose
`cil_list.c` implements a simple singly linked list used throughout CIL for expressions, datum lists, classperms, AST helper collections, and temporary traversal results.

## Important APIs, Types, And Functions
The file implements initialization/destruction (`cil_list_init`, `cil_list_destroy`, `cil_list_item_init`, `cil_list_item_destroy`), mutation (`cil_list_append`, `cil_list_prepend`, `cil_list_insert`, `cil_list_append_item`, `cil_list_prepend_item`, `cil_list_remove`), and predicates (`cil_list_contains`, `cil_list_match_any`). `cil_list_error` logs an error and terminates on impossible misuse.

## Control Flow
Append/prepend allocate a new item and update head/tail. Insert can prepend, append, or link after a supplied current item. Append/prepend item variants accept an existing chain and find its last node before splicing. Destroy recursively destroys nested lists when item flavor is `CIL_LIST`; otherwise it optionally destroys item data through `cil_destroy_data`.

## State And Persistence Behavior
List state is heap memory only. Items carry a `flavor` tag and raw `data` pointer; ownership is controlled by the caller and the `destroy_data` flag. No persistence exists outside objects that reference these lists.

## Dependencies And Integration Points
The implementation depends on `cil_mem` for allocation, `cil_log` for fatal list misuse, `cil_flavor` for tags, and `cil_destroy_data` for optional payload destruction. Almost every CIL subsystem uses these lists.

## Risks And Edge Cases
The API is not defensive for NULL lists in mutators; misuse exits the process. `cil_list_match_any` compares pointer identity and flavor, not semantic equality. Splicing existing chains assumes the chain is well-formed and acyclic. Destroying with the wrong `destroy_data` value can leak memory or double-free shared AST data.

## Test Signals
Tests should cover empty-list append/prepend, tail updates after remove, insertion at front/middle/end, nested-list destruction, pointer-identity matching, and sanitizer runs over AST build/destroy paths.
