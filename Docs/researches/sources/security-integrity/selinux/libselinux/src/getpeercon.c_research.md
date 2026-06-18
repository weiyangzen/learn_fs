# sources/security-integrity/selinux/libselinux/src/getpeercon.c

Purpose: Retrieves the SELinux security context of a connected socket peer.

Important APIs/types/functions: `getpeercon_raw()` uses `getsockopt(SO_PEERSEC)`. `getpeercon()` translates the raw result.

Control flow: allocates an initial buffer, calls `getsockopt`, resizes to kernel-provided size on `ERANGE`, and returns 0 on success with caller-owned context.

State and persistence: read-only socket metadata.

Dependencies and integration: depends on `SO_PEERSEC` availability and raw/trans conversion.

Risks and test signals: tests should cover connected UNIX sockets, ERANGE resize, unsupported socket types, translation failure, and fallback constant definition for platforms lacking `SO_PEERSEC`.
