## sources/security-integrity/audit-userspace/audisp/plugins/ids/account.h

Purpose: account model API for audisp-ids.

It defines `account_data_t` with embedded AVL node, immutable name pointer, and karma, then declares lifecycle, lookup, mutation, traversal, and scoring functions. State is managed by `account.c`'s global index. Dependencies are `avl.h` and stdio for dumps. Risks are requiring `avl` as the first struct member and exposing mutable account pointers. Tests should validate callers do not stack-allocate transient names without duplication.
