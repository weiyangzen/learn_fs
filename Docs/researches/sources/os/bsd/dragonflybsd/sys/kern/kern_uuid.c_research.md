# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_uuid.c

Implements kernel UUID generation, formatting, comparison, nil/type checks, endian encoding/decoding, and string parsing.

Key state:
- `uuid_last`: last generated UUID state, including timestamp, sequence, and node.
- `uuid_lock`: serializes generation.

Key APIs:
- `kern_uuidgen()`
- `sys_uuidgen()`
- `snprintf_uuid()`, `printf_uuid()`, `sbuf_printf_uuid()`
- `kuuid_compare()`, `kuuid_is_nil()`, `kuuid_is_ccd()`, `kuuid_is_vinum()`
- `le_uuid_enc()`, `le_uuid_dec()`, `be_uuid_enc()`, `be_uuid_dec()`
- `parse_uuid()`

Important behavior:
- `uuid_node()` attempts to obtain an Ethernet MAC via `if_getanyethermac()`, falls back to random bytes, and sets multicast/local-style low bit behavior.
- `uuid_time()` builds a 60-bit count of 100 ns units since the Gregorian UUID epoch using `nanotime()`.
- `kern_uuidgen()` generates version-1 UUIDs under lock, choosing a new random 14-bit sequence when node changes or state is uninitialized, incrementing sequence if time goes backwards or repeats, and reserving a range for `count`.
- `sys_uuidgen()` limits batch generation to 1..2048 UUIDs, allocates temporary kernel memory, generates, and copies out.
- Formatting prints canonical `8-4-4-4-12` hex groups.
- `kuuid_compare()` treats NULL as nil and orders fields lexicographically.
- `kuuid_is_ccd()` and `kuuid_is_vinum()` compare against DragonFly GPT partition type UUIDs.
- Encoding/decoding routines serialize UUIDs to little-endian and big-endian byte streams.
- `parse_uuid()` accepts empty string as nil, otherwise requires the modern 36-character dashed form and validates variant bits.

Filesystem relevance:
- Relevant for storage/filesystem metadata that uses UUIDs, including GPT partition type checks for DragonFly CCD and Vinum.
- Provides common UUID parsing/encoding helpers usable by filesystem and block-device code.
