# File Research: sources/os/plan9/plan9/sys/src/9/pc/bios32.c

BIOS32 service directory discovery and calling-interface setup.

Key responsibilities:
- Defines BIOS32 service directory and service interface structures.
- Scans BIOS memory for `_32_` on 16-byte boundaries and validates checksum.
- Maps the BIOS32 entry point with `vmap` and constructs a far pointer using `KESEL`.
- `bios32open(id)` calls the BIOS32 service directory for a four-character service ID, maps the returned service base, and builds a callable far pointer for the service entry.
- `bios32ci()` serializes BIOS32 service calls with `bios32lock`.
- `BIOS32close()` unmaps service memory and frees the descriptor.

Important behavior:
- Uses little-endian field extraction for the directory physical address.
- Lazily locates BIOS32 on first open.
- Uses a static debug flag macro, disabled by default.

Dependencies:
- Depends on low BIOS memory mapping macros, `vmap`/`vunmap`, `bios32call`, and `KESEL`.

Notable risks:
- BIOS32 calls are globally serialized, but service-specific behavior still depends on firmware correctness.
- `vmap(L32GET(...), 4096+1)` maps one page plus one byte, likely to cover potential page crossing.
