# File Research: sources/os/plan9/9front/sys/src/9/ip/nullmedium.c

Defines null and temporary unbound IP media.

Key elements:
- `nullmedium` has no-op bind/unbind and a write path that frees the block then errors.
- `unboundmedium` is a sentinel used while bind/unbind transitions are in progress.
- Registers `nullmedium` with the IP media table.

Dependencies:
- Used by `ipifc.c` during bind/unbind state transitions.

Research notes:
- The sentinel prevents code from treating an interface as fully usable while medium operations are still underway.
