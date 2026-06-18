# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdouble.c

Implements double-precision floating point operators using 8-byte strings as double containers.

Arithmetic operators include `.dadd`, `.ddiv`, `.dmul`, and `.dsub`. Simple functions include `.dabs`, `.dceiling`, `.dfloor`, `.dneg`, `.dround`, `.dsqrt`, and `.dtruncate`. Transcendentals include `.darccos`, `.darcsin`, `.datan`, `.dcos`, `.dexp`, `.dln`, `.dlog`, and `.dsin`.

Comparison operators include `.deq`, `.dge`, `.dgt`, `.dle`, `.dlt`, and `.dne`.

Conversion operators include `.cvd`, `.cvsd`, `.dcvi`, `.dcvr`, and `.dcvs`.

`double_params()` accepts real, integer, or readable 8-byte string operands. `double_params_result()` validates writable 8-byte result strings. `double_result()` writes the result into the supplied string and collapses stack operands.

Notable behavior: `.cvsd` does strict string syntax filtering before `sscanf`; `.dcvs` first prints with `%g` and retries with `%.16g` if needed for accuracy.

Operator definitions are split into `zdouble1_op_defs` and `zdouble2_op_defs`.
