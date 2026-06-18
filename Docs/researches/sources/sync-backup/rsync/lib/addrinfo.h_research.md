# sources/sync-backup/rsync/lib/addrinfo.h

Purpose: supplies missing `getaddrinfo`/`getnameinfo` constants, structs, and prototypes on platforms without full modern socket API support, using PostgreSQL-derived compatibility code.

Important APIs/types/functions: defines fallback `EAI_*`, `AI_*`, `NI_*`, `NI_MAXHOST`, `NI_MAXSERV`, `struct addrinfo`, and `struct sockaddr_storage` where missing. When `HAVE_GETADDRINFO` is absent, it macro-renames `getaddrinfo`, `freeaddrinfo`, `gai_strerror`, and `getnameinfo` to private `pg_*` names and declares them.

Control flow: preprocessor-only feature detection. The header avoids conflicts with partial system support: if headers lack `struct addrinfo`, rsync uses its local struct; if libc lacks functions, it exposes local implementations under renamed symbols.

State and persistence behavior: no runtime state. It shapes ABI expectations at compile time and therefore must match `lib/getaddrinfo.c` and all socket callers.

Dependencies/integration: included through rsync portability headers before socket code uses address-resolution APIs. It integrates with configure probes such as `HAVE_STRUCT_ADDRINFO`, `HAVE_GETADDRINFO`, and `HAVE_STRUCT_SOCKADDR_STORAGE`.

Risks/test signals: macro renaming can surprise code that expects system symbols, and the fallback constants may not match all platform-specific values. Build tests on systems with partial `getaddrinfo` support are important, as are socket tests for numeric host/service flags and canonical-name requests.
