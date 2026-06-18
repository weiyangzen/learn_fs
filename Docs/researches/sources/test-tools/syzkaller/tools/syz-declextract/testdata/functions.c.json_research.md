# sources/test-tools/syzkaller/tools/syz-declextract/testdata/functions.c.json

Purpose: this golden JSON represents extracted function graph and syscall metadata for `functions.c`.

Important structure: top-level keys are `functions` and `syscalls`. Functions include `__do_sys_functions`, helper functions from `fs.h` and `types.h`, `func_bar`, `func_baz`, `func_foo`, `func_qux`, `typing`, and `typing1`. The syscall entry exposes `__do_sys_functions`.

Control-flow and facts: `__do_sys_functions` records calls to `__fget_light` and `func_baz`, argument 0 flowing into `__fget_light`, and `func_baz` return flowing to syscall return. `func_baz` records calls to `func_foo`, `func_bar`, `from_kuid`, and `alloc_fd`, with return facts from the latter helpers. The typing functions provide a compact data-flow case for struct-field/local-variable propagation.

State and persistence: static cache input for tests. It must remain synchronized with source line numbers and function names.

Risks and test signals: validates call graph and return fact extraction but does not include constants or structs as top-level outputs. It is useful for catching accidental pruning of static helpers and builtin handling regressions.
