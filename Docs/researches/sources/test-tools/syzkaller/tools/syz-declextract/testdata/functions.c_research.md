# sources/test-tools/syzkaller/tools/syz-declextract/testdata/functions.c

Purpose: this fixture tests function call graph extraction, return-value facts, builtin handling, syscall-to-helper flows, and simple typed field assignment facts.

Important APIs and flow: static `func_foo` is called by `func_bar`; `func_baz` calls `func_foo`, conditionally calls `func_bar`, ignores a `__builtin_constant_p` branch for practical reachability, and returns either `from_kuid()` or `alloc_fd()`. `func_qux` returns a local fd. `SYSCALL_DEFINE1(functions, long x)` passes `x` to `__fget_light` and returns `func_baz(1)`. `struct Typed`, `typing1`, and `typing` model simple struct pointer field reads/writes and local variable propagation.

State and persistence: no persistence; local variables and struct fields are used to test data-flow facts.

Dependencies and integration: includes fixture `fs.h`, `syscall.h`, and `types.h` for helper functions, syscall macros, and atomic helpers.

Risks: source is synthetic and intentionally tiny; real kernel call graphs have indirect calls and macro-generated functions not represented here.

Test signals: paired JSON includes function list, call edges, return facts from helpers to `func_baz` and from `func_baz` to the syscall, syscall argument-to-helper facts, and typed assignment information.
