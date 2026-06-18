# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/util.h

This header defines shared FMA utility constants and kernel-only ereport transport helpers.

Shared constants:
- `FM_MAX_CLASS` is 100.
- Error channel is `"com.sun:fm:error"`.
- Kernel event publisher is `"fm"`.

Dump-device ereport transport:
- Ereport dump records use `ERPT_MAGIC`.
- Limits include maximum errors, data size, event channel size, and high-water mark.
- `erpt_dump_t` is a fixed-layout header followed by packed native nvlist data. It includes magic, checksum, size, reserved padding, high-resolution time, high-resolution base, and corresponding wall-clock base time.
- Comments emphasize identical representation for 32-bit and 64-bit producers/consumers.

Kernel-only definitions:
- Stack depth and symbol size constants for stack payloads.
- Errorq drain PIL.
- Stack payload field name.
- Externs for `ereport_errorq`, dump buffer, and dump length.
- Function declarations for FM init, nvlist printing, panic/banner, dump/post, stack payload addition, and `is_fm_panic()`.

Dependencies and relationships:
- Includes `sys/nvpair.h` and `sys/errorq.h`.
- Works with `sys/fm/protocol.h` event construction by providing kernel transport, panic, and dump support.
