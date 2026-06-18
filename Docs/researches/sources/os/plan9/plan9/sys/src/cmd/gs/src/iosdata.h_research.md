# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iosdata.h

Operand-stack data wrapper for Ghostscript.

Key behavior:
- Includes `isdata.h`.
- Defines `op_stack_t` as a wrapper containing a generic `ref_stack_t`.
- Defines `public_st_op_stack()` GC descriptor macro as a suffix of `st_ref_stack`.
- Defines `st_op_stack_num_ptrs`.

Research notes:
- The operand stack is currently just a generic ref stack; this wrapper gives it a distinct public structure descriptor and type identity.
