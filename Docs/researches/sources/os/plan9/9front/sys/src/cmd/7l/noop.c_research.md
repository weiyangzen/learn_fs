# File Research: sources/os/plan9/9front/sys/src/cmd/7l/noop.c

Late instruction cleanup and function prologue/epilogue expansion for ARM64.

Key functions:
- `noops` performs several final rewrites over the instruction list.
- `nocache` clears cached instruction-class/optab data after an instruction is rewritten.

Main `noops` responsibilities:
- Finds leaf subroutines by clearing `LEAF` on calls.
- Tracks frame size and `BECOME` argument-space requirements.
- Removes `ANOP` instructions and retargets branches around them.
- Defines `ALEFbecome` with the maximum become size.
- Increases caller frame sizes when a function may call a `BECOME` target.
- Aligns stack frames to `STACKALIGN`.
- Expands `ATEXT` into stack adjustment and link-register save sequences.
- Expands `ARETURN` into restore, stack adjustment, and `ARET`.
- Expands special `RETURN $n` forms into branch/become sequences.

Important details:
- Leaf functions with no frame can avoid save/restore.
- Large stack frames are split between pre/post-indexed link-register operations and explicit `ADD`/`SUB`.
- Rewritten instructions must have caches cleared because operand classes and optab selections are no longer valid.

Filesystem relevance: indirect toolchain code.
