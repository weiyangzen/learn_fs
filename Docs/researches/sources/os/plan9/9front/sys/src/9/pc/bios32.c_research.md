# File Research: sources/os/plan9/9front/sys/src/9/pc/bios32.c

BIOS32 Service Directory discovery and call wrapper.

Key responsibilities:
- Searches for the `_32_` BIOS32 Service Directory header.
- Maps the BIOS32 entry point and constructs far pointers using kernel code selector `KESEL`.
- Opens specific BIOS32 services by ID, maps their service regions, and builds callable service far pointers.
- Provides serialized `bios32ci()` calls and `bios32close()` cleanup.

Important behavior:
- Service IDs are packed little-endian into EAX before calling the BIOS32 directory.
- A nonzero low byte of EAX after the directory call means service lookup failed.
- All BIOS32 calls are protected by `bios32lock`.

Dependencies:
- Depends on `sigsearch`, `vmap`/`vunmap`, `bios32call` assembly support, and `BIOS32ci` from `dat.h`.

Notable risks:
- Maps service memory lengths supplied by firmware.
- A small verbose flag exists but is disabled by default.
