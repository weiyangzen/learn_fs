# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/authunix_prot.c

Read completely: 84 lines.

This file implements `xdr_authunix_parms`, the XDR codec for `struct authunix_parms`.

Key behavior: encodes/decodes/frees timestamp, machine name bounded by `MAX_MACHINE_NAME`, uid, gid, and group array bounded by `NGRPS`.

Important interactions: used by `auth_unix.c` to serialize original credentials and refresh/free decoded credential structures.

Security/reliability notes: correctness depends on XDR bounds constants; no additional policy validation is performed here.
