## sources/security-integrity/audit-userspace/audisp/plugins/ids/avl.c

Purpose: allocation-free AVL tree implementation for IDS indexes.

It provides `avl_init`, `avl_search`, `avl_insert`, `avl_remove`, in-order traversal, iterator first/next, and tree intersection. Control flow links caller-embedded `avl_t` nodes directly, maintains balance factors, and uses fixed-height stacks sized by `AVL_MAX_HEIGHT`. State is entirely caller-owned tree/node links. Dependencies are comparison callbacks and `avl.h`; no pthread locking by design. Risks include complex rotation correctness, no assertions in production, stack height assumptions, intrusive node requirement, and no duplicate ownership management beyond returning existing node. Tests should cover insert/delete rotation cases, duplicates, iteration order, and intersection.
