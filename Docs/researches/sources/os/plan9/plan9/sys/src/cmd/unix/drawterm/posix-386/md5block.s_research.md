# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/md5block.s

Generated i386 assembly implementation of `__md5block`. It processes 64-byte MD5 blocks, maintaining the four MD5 state words and applying all four MD5 rounds with constants and rotate counts expanded inline.

Key behavior:
- Saves/restores callee-saved registers.
- Iterates from input pointer to end pointer in 64-byte steps.
- Adds transformed `a/b/c/d` values back into the digest state.
- Uses little-endian 32-bit block words directly from memory.

Notable role: architecture-specific performance path for MD5 in drawterm/libsec.
