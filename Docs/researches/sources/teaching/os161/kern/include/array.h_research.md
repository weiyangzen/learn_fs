# File Research: sources/teaching/os161/kern/include/array.h

Defines OS/161's generic dynamic pointer array and typed-array macro system.

Key APIs:
- Base `struct array` stores `void **v`, `num`, and `max`.
- Provides create/destroy/init/cleanup, num/get/set, preallocate, setsize, add, remove.
- Inline get/set/add include optional `KASSERT` checks via `ARRAYS_CHECKED`.

Typed arrays:
- `DECLARRAY_BYTYPE`/`DEFARRAY_BYTYPE` generate typed wrapper structs and typed accessors around the base array.
- `DECLARRAY`/`DEFARRAY` are shorthand for arrays of `struct T *`.
- Defines `stringarray`.

Relevance:
- `semfs` uses generated arrays for semaphores and directory entries.
- SFS uses vnode arrays declared elsewhere using this infrastructure.
