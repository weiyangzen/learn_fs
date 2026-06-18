# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/opcheck.h

`opcheck.h` defines macros for operand and object validation in Ghostscript operator implementations. It requires interpreter allocation, ref, and error definitions from headers such as `ialloc.h`, `iref.h`, and `ierrors.h`.

The macros check object type, structure type, array type, procedure-ness, access permissions, combined type/access constraints, and integer bounds. Most failures return Ghostscript errors such as `e_typecheck`, `e_invalidaccess`, or `e_rangecheck`.

`check_proc_failed` is declared for procedure validation that may also account for stack underflow. The macros are designed for operator bodies that return immediately on invalid operands, so callers must use them only in functions where `return_error(...)` is valid.
