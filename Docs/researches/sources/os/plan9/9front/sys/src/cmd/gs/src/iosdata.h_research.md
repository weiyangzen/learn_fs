# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iosdata.h

Operand-stack data header.

Key contents:
- Includes `isdata.h`.
- Defines `op_stack_t` as a wrapper around a generic `ref_stack_t`.
- Defines `public_st_op_stack`, a GC structure descriptor macro layered on `st_ref_stack`.
- Defines `st_op_stack_num_ptrs` as the same pointer count as `st_ref_stack`.

Notable dependencies:
- `isdata.h` and the ref-stack GC descriptor machinery.

Research notes:
- The operand stack currently has no extra fields beyond the generic ref stack.
- The wrapper type exists so the operand stack can have a distinct structure descriptor and API identity.
