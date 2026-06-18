# sources/test-tools/kdevops/scripts/kconfig/list_types.h

## Purpose
This header declares the minimal list node structures shared by list and hash table utilities.

## Important APIs, Types, And Functions
It defines `struct list_head` with `next` and `prev`, `struct hlist_head` with `first`, and `struct hlist_node` with `next` and `pprev`.

## Control Flow
There is no runtime flow; it is type-only.

## State And Persistence
Instances of these structs are embedded in higher-level objects and hold in-memory linkage state only.

## Dependencies And Integration Points
It is included by `list.h` and `expr.h`, making it foundational for symbol/menu/property collections.

## Risks And Test Signals
Any ABI or field-name change breaks all list macros. Compile tests across all Kconfig objects are the main signal.
