# sources/sync-backup/rsync/lib/inet_ntop.c

Purpose: fallback `inet_ntop` implementation for formatting IPv4 and, when available, IPv6 binary addresses into presentation strings.

Important APIs/types/functions: public `inet_ntop`, static `inet_ntop4`, optional static `inet_ntop6`, and constants `NS_INT16SZ` and `NS_IN6ADDRSZ`.

Control flow: `inet_ntop` switches on address family, calling IPv4 or IPv6 helpers or setting `errno = EAFNOSUPPORT`. IPv4 uses `snprintf` into a dotted-quad temporary and checks destination capacity. IPv6 converts bytes to 16-bit words, finds the longest zero run for `::` compression, detects IPv4-embedded forms, formats hex groups, handles trailing zero compression, verifies capacity, and copies to the caller buffer.

State and persistence behavior: no state. All formatting uses caller-provided destination storage and stack temporaries.

Dependencies/integration: includes `rsync.h` for socket definitions, errno, `snprintf`, and assertions. Used by socket/address code when libc lacks `inet_ntop`.

Risks/test signals: IPv6 availability is gated by `AF_INET6` while `inet_pton.c` uses `INET6`, so configure consistency matters. Capacity checks must cover exact-fit destinations. Tests should compare system `inet_ntop` for IPv4, zero-compressed IPv6, IPv4-mapped IPv6, unsupported families, and too-small buffers.
