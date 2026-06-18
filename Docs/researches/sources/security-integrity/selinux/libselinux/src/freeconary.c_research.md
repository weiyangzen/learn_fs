# sources/security-integrity/selinux/libselinux/src/freeconary.c

Purpose: Frees NULL-terminated arrays of context strings returned by libselinux APIs.

Important APIs/types/functions: `freeconary(char **con)` iterates until a NULL sentinel, frees each element with `free()`, then frees the array.

Control flow: NULL array input returns immediately.

State and persistence: releases caller-owned arrays.

Dependencies and integration: used by user-context APIs and cleanup paths in compute/list functions.

Risks and test signals: arrays must be NULL-terminated. Tests should cover NULL input, empty array, multi-entry arrays, and cleanup after partially built arrays.
