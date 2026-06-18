# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/auth_unix.c

Read completely: 389 lines.

This file implements legacy AUTH_UNIX/AUTH_SYS client authentication: `authunix_create`, `authunix_create_default`, `set_rpc_maxgrouplist`, and auth ops.

Key behavior: `authunix_create` serializes timestamp, machine name, uid, gid, and group list with `xdr_authunix_parms`, stores original credentials, and pre-marshals credential/verifier pairs. `authunix_create_default` gathers hostname, effective uid/gid, and groups, truncating groups to `maxgrplist`. `authunix_validate` accepts server-provided `AUTH_SHORT` shorthand credentials. `authunix_refresh` falls back from shorthand to original credentials with a fresh timestamp. Destroy frees original/shorthand credentials, verifier storage, private data, and handle.

Important interactions: used by RPC broadcast and callers needing UNIX-style credentials; depends on `authunix_prot.c` XDR and shared RPC locks for ops initialization.

Security/reliability notes: comments explicitly state this scheme is weak: credentials are unencrypted and client-asserted. Some ids are cast to `int`, and timestamp uses `u_long` seconds with a 32-bit truncation comment.
