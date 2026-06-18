# sources/security-integrity/selinux/libselinux/src/freecon.c

Purpose: Implements the public deallocator for SELinux context strings returned by libselinux APIs.

Important APIs/types/functions: `freecon(char *con)` simply calls `free(con)`.

Control flow: no special handling beyond libc `free`, so NULL is allowed by libc semantics.

State and persistence: releases caller-owned heap memory.

Dependencies and integration: all APIs returning context strings document `freecon()` as the release method, allowing ABI flexibility even though current implementation is `free`.

Risks and test signals: low risk. Tests should verify callers consistently use `freecon()` for returned contexts and no mismatched allocator is introduced.
