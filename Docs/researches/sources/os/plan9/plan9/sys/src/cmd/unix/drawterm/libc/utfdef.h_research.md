# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfdef.h

This header supplies standalone type aliases for UTF code.

Key contents:
- Temporarily maps Plan 9 type names to `_utf*` names and typedefs byte/integer aliases.
- Defines `nelem` and `nil`.

Important details:
- Used to compile UTF components in environments where Plan 9 base headers may conflict.
