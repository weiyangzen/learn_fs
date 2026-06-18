# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_uuid.c

## Purpose
Implements kernel UUID generation, UUID string formatting/parsing/validation, endian encode/decode helpers, and MAC-address node management for time-based version 1 UUIDs.

## Key Interfaces
- `kern_uuidgen()` generates one or more version 1 UUIDs.
- `sys_uuidgen()` copies a bounded batch of generated UUIDs to userland.
- `uuid_ether_add()` and `uuid_ether_del()` maintain candidate hardware node identifiers.
- `snprintf_uuid()`, `printf_uuid()`, and `sbuf_printf_uuid()` format UUIDs.
- `le_uuid_enc()`, `le_uuid_dec()`, `be_uuid_enc()`, and `be_uuid_dec()` serialize/deserialize UUIDs.
- `validate_uuid()`, `parse_uuid()`, and `uuidcmp()` validate, parse, and compare UUIDs.

## State And Locking
`uuid_mutex` protects the last generated UUID state and the small `uuid_ether[]` node-address array. `uuid_last` stores native-order time and sequence state for monotonic generation. Up to four node addresses are tracked; if no unique Ethernet address exists, a random multicast node is synthesized.

## Control Flow
`uuid_node()` returns the first known node address, creating a random multicast address if needed. `uuid_time()` converts current time to 100-nanosecond intervals since the UUID Gregorian epoch. `kern_uuidgen()` locks the generator, selects or advances the 14-bit sequence based on node/time monotonicity, reserves the requested count by updating `uuid_last`, then fills caller storage with incrementing time values and version/variant bits. MAC add/delete validate globally unique nonzero addresses and maintain the preferred node order. String parsing accepts the modern 36-character hyphenated form and can optionally allow empty strings as nil UUIDs or check variant semantics.

## Integration Notes
Used by kernel and syscall consumers needing UUIDs. It depends on `arc4random()`, `bintime()`, endian helpers, `sbuf`, copyout, and network interface MAC registration hooks elsewhere.

## Risks
Generation is version 1 UUID style, so the preferred real MAC address can be embedded when available; privacy-sensitive consumers should account for that. `sys_uuidgen()` enforces `UUIDGEN_BATCH_MAX`, but `kern_uuidgen()` assumes the caller passes a sensible count. String validation relies on fixed-length formatting plus `sscanf()` conversions and does not support older dotted UUID syntax.
