# sources/user-network-fs/libsmb2/lib/compat.h

Purpose: Centralizes portability typedefs, macros, includes, errno aliases, socket abstractions, missing POSIX declarations, and platform-specific replacements.

Important APIs/types/functions: Defines `t_socket`, `SMB2_VALID_SOCKET`, `SMB2_INVALID_SOCKET`, substitute `struct addrinfo`, `struct pollfd`, `struct sockaddr_storage`, `struct iovec`, declarations for fallback `poll`, `writev`, `readv`, `getaddrinfo`, `freeaddrinfo`, `getlogin_r`, `random`, `srandom`, and platform-specific remaps such as `close`, `connect`, `read`, `write`, and Nintendo/Amiga network wrappers.

Control flow: Preprocessor branches select definitions for Windows/Xbox, Pico, Dreamcast, Amiga, PS2, PS3, BSDs, Linux, Apple, Vita, Nintendo platforms, ESP, and Android. The final section supplies missing `O_*`, `ENOMEM`, `EINVAL`, and `typeof` definitions.

State/persistence: No runtime state, but it mutates the compilation environment heavily through macros. Some macros replace standard functions globally after inclusion.

Dependencies/integration: Included by nearly every libsmb2 C file. It must be ordered carefully with system headers because it defines replacement structures and function-like macros.

Risks: Macro substitution can surprise downstream code, especially `strncpy(a,b,c) strcpy(a,b)` on Amiga, `close`, `read`, `write`, and network symbol remaps. Struct definitions may diverge from platform ABI if native headers are partially present. Windows include ordering around winsock headers is fragile. Global `typeof` definition assumes GCC-compatible `__typeof__` where absent.

Test signals: Multi-platform compile matrix is the main signal. Static analysis should inspect macro pollution, duplicate type definitions, and include-order regressions. Runtime smoke tests should cover socket open/connect/read/write/poll on each supported target.
