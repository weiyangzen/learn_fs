# File Research: sources/os/bsd/openbsd-src/sbin/iked/dh.h

`dh.h` declares the key-exchange abstraction used by iked. It defines group types for MODP, ECP, Curve25519, and SNTRUP761X25519, plus `group_id` metadata and `dh_group` runtime state.

`dh_group` carries backend-specific state pointers and function pointers for init, exchange length, optional secret length, fixed-buffer exchange/shared operations, and ibuf-based exchange/shared operations for variable hybrid KEM exchanges.

The public API includes group initialization/freeing, group lookup by IKE group ID, and creation of exchange/shared-secret buffers. `DH_MAXSZ` documents the 8192-bit maximum classic DH size.
