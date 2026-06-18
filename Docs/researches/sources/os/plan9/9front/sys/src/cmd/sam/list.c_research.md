# File Research: sources/os/plan9/9front/sys/src/cmd/sam/list.c

`list.c` is a small generic growable-list implementation used throughout sam for pointer lists and position lists.

`growlist` lazily allocates storage in `INCR` chunks and expands when full, zeroing the new tail. List type `'p'` stores `void*`; type `'P'` stores `Posn`.

`inslist` inserts at an index using varargs to receive either a pointer or `Posn`, shifts later entries right, and increments `nused`.

`dellist` removes an indexed element, shifts later entries left, and decrements `nused`. `listalloc` creates an empty typed list; `listfree` frees storage and the list object.
