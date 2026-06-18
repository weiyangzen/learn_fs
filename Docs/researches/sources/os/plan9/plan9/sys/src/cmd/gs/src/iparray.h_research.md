# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparray.h

Small bridge header for packed-array construction.

Key behavior:
- Exists because packed-array construction needs both `ipacked.h` and `istack.h`.
- Declares `make_packed_array`, implemented in `zpacked.c`.
- The function builds a packed array from the top N stack elements using dual VM memory and a client allocation name.

Research notes:
- This header intentionally avoids placing cross-dependencies in either `ipacked.h` or `istack.h`.
