# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/aux.c

This file provides small common mail utility helpers for unsafe-character handling, mailbox path behavior, and temporary-error detection.

Key behavior:
- `shellchars` detects carriage-return/newline characters in a C string.
- `escapespecial` percent-escapes shell-special characters using `%%HH`, replacing and freeing the input `String`.
- `unescapespecial` reverses those escapes when they decode to non-high-bit values.
- `hexchar` and `hex2uint` implement nibble conversion.
- `returnable` treats `/dev/null` as non-returnable.
- `temperror` checks the current error string for transient upas activity/problem messages.

Integration and risks:
- Uses Plan 9 `String` routines from `<String.h>` through `common.h`.
- Escape decoding has loose validation: bad hex returns large unsigned values and is handled as non-decodable high-bit-ish data.
