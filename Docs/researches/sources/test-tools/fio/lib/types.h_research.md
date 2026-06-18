# sources/test-tools/fio/lib/types.h

Purpose: portability typedefs for bool and kernel async IO flags.

Important APIs/types: defines `bool`, `false`, and `true` when `CONFIG_HAVE_BOOL` is absent and not compiling as C++; otherwise includes `stdbool.h`. Defines `__kernel_rwf_t` as `int` when the platform lacks it.

Control flow/state: compile-time compatibility only; no runtime behavior.

Dependencies/integration: included by many fio utility headers so they can use bool consistently across C/C++ and old systems.

Risks/test signals: macro/config mismatches can conflict with system definitions. Compile matrix coverage across C, C++, and platforms with/without kernel `rwf_t` is the main signal.
