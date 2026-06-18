# sources/user-network-fs/libtirpc/tirpc/rpc/types.h

Purpose: `types.h` defines core RPC scalar types, boolean constants, allocation macros, compatibility typedefs, transport address buffers, bind-address structs, and internal socket metadata.

Important APIs, types, and functions: It defines `bool_t`, `enum_t`, `rpcprog_t`, `rpcvers_t`, `rpcproc_t`, `rpcprot_t`, `rpcport_t`, `rpc_inline_t`, `TRUE`, `FALSE`, `mem_alloc`, `mem_free`, compatibility typedefs for `u_char`, `u_short`, `u_int`, `u_long`, `quad_t`, `u_quad_t`, `daddr_t`, `caddr_t`, `struct netbuf`, `struct t_bind`, and `struct __rpc_sockinfo`.

Control flow: There is no runtime control flow. Preprocessor branches adapt typedefs for Apple, FreeBSD, non-glibc, Bionic, and libc feature macros.

State and persistence behavior: No state is declared. `mem_alloc` and `mem_free` map directly to `calloc` and `free`, which affects allocation initialization across XDR and transport code.

Dependencies and integration points: It includes system types/time/param, stdlib, and `netconfig.h`. Nearly every libtirpc header and source depends on these base definitions.

Risks: Typedef guards must avoid conflicting with libc definitions. `mem_free(ptr, bsize)` ignores size through the macro, but callers often pass sizes for historical allocators. `struct netbuf` ownership rules are convention-based and not encoded in the type.

Test signals: Build tests should cover supported libc/platform macro combinations, verify RPC scalar widths, ensure `mem_alloc` zero-initializes, and check `netbuf`/`__rpc_sockinfo` ABI layout expected by implementation code.
