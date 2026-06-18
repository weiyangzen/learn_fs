# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/ahd.c

This file implements support for the encrypted American Heritage Dictionary backend.

Key behaviors:
- `ahdprintentry()` decrypts entry bytes by XORing each byte with `(addr++ >> 1) & 0xff`.
- Initializes a 256-entry translation table to map special encoded bytes to runes such as accented characters, degree sign, and middle dot.
- Parses inline tags delimited as `%@TAG@%`.
- For command `h`, stops output at tag `EH`.
- For command `r`, preserves tag syntax in output.
- Otherwise emits decoded text through dictionary output helpers.
- `ahdnextoff()` scans encrypted bytes for entry-boundary marker patterns `%@NL@%` and `%@2@%`.
- `ahdprintkey()` reports no pronunciations.

Notable implementation details:
- Temporarily changes `breaklen` to 80 while printing AHD entries.
- Uses a small state machine: `Run`, `Openper`, `Openat`, `Closeat`.
- `ahdnextoff()` returns a definition offset fallback if the second marker is not found.
