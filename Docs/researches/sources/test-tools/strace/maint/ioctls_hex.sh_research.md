# sources/test-tools/strace/maint/ioctls_hex.sh

Purpose: extracts ioctl constants defined directly as hexadecimal command numbers from selected header files.

Important APIs/types/functions: accepts include directory, type regex, and header paths; constructs a define regex; greps both plain and `uapi/` paths; sed formats entries as `{ "header", "NAME", 0, VALUE, 0 },`.

Control flow: validate arguments, `cd` into include directory, search each requested file for matching `#define` lines, normalize `uapi/` prefixes, format entries, and sort unique.

State and persistence behavior: no writes; stdout is generated table content.

Dependencies and integration points: called repeatedly by `ioctls_gen.sh` for known ioctl families that are easier to detect by command-number high byte.

Risks: only direct hex literals matching `0xTYPE..` are captured; symbolic `_IO*` definitions are intentionally handled elsewhere. Regex type argument can be broad and may include false positives.

Test signals: grep counts in `ioctls_gen.sh` and generated entries for hdreg, fb, loop, cdrom, termios, sockios, wireless, and related headers.
