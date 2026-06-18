# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/block.c

Small PPP block allocator. `allocb` allocates a `Block` with 128 bytes of leading pad for protocol/header prepending, `resetb` positions read/write pointers after the pad, and `freeb` poisons pointers before freeing blocks whose data buffer is inline with the `Block`.
