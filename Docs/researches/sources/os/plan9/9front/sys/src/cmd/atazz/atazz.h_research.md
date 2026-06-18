# File Research: sources/os/plan9/9front/sys/src/cmd/atazz/atazz.h

Shared declarations for the `atazz` ATA diagnostic/command shell.

Important contents:
- Defines command flavor flags, device state, request/reply command packets, and request execution state.
- Declares formatter functions for signatures, identify data, I/O dumps, SMART, SCT, and logs.
- Defines tables for bit names, text command names, feature-entry decoding, SCT pseudo-registers, and ATA command metadata.
- Declares endian helpers and device/probe entry points.

The header bridges Plan 9 `fis.h` ATA FIS definitions with the command interpreter.
