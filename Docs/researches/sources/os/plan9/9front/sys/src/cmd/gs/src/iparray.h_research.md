# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iparray.h

Small interface header for packed-array construction.

Key contents:
- Explains that the header exists to avoid forcing `ipacked.h` and `istack.h` to include each other.
- Declares `make_packed_array`, implemented in `zpacked.c`, which creates a packed array from the top `N` stack elements.

Notable dependencies:
- Requires packed-array and stack types from `ipacked.h` and `istack.h` in the including context.

Research notes:
- This is a dependency-separation shim.
- Packed-array construction is tied to interpreter stack state and dual-memory allocation.
