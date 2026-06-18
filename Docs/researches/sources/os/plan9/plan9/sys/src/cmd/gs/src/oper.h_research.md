# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/oper.h

Ghostscript interpreter header for PostScript operator definitions and common operator checks.

It includes operand stack, operator declaration, operator definition, error, check, and utility headers. The file documents the operator procedure contract: operators receive an `i_ctx_t *` and return `0`, a negative Ghostscript error code, or one of several positive interpreter-control codes.

Key contents:

- Declares `check_type_failed(const ref *)`, used to convert failed type checks on operand-stack guard entries into `stackunderflow`.
- Defines macros for type/access checking: `check_type`, `check_stype`, `check_array`, `check_type_access`, `check_read_type`, and `check_write_type`.
- Defines `return_op_typecheck` and `NYI`.
- Defines special positive return values `o_push_estack`, `o_pop_estack`, and `o_reschedule`.

The file is central to interpreter operator implementation discipline. It is not filesystem-related.
