# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/group.h

Small header defining group table structures and lookup APIs for ext4srv permission handling.

Key behavior:
- `Group` contains a 32-bit ID, name pointer, dynamic member array, and member count.
- `Groups` contains the duplicated raw text backing store, group array, and group count.
- Declares parsing, cleanup, name lookup, ID lookup, and membership-check functions.

Notable dependencies:
- Assumes Plan 9 integer typedefs such as `u32int` are available before inclusion.
- Implemented by `group.c` and consumed by `ext4srv.c` plus partition setup code.

Research notes:
- The header intentionally exposes raw arrays rather than hiding them behind an opaque type.
