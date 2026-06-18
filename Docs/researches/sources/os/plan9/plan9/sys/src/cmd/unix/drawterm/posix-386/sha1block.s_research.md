# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/sha1block.s

Generated i386 assembly implementation of `__sha1block`. It processes SHA-1 64-byte blocks, expands the 80-word schedule on the stack, applies all SHA-1 rounds, and folds results into the five-word state.

Key behavior:
- Converts input words with byte swaps to SHA-1 big-endian order.
- Uses unrolled groups for the four SHA-1 round functions/constants.
- Saves/restores i386 callee-saved registers.

Notable role: architecture-specific SHA-1 acceleration for drawterm/libsec.
