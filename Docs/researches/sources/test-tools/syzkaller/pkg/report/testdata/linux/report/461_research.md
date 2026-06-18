# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/461

Purpose: golden fixture for a stack segment fault in early init. Expected title is `stack segment fault in kernel_init`, type is `DoS`, and `PANICKED: Y`.

Important APIs, types, and functions: parser coverage includes x86 exception wording outside the usual BUG/WARNING forms. Kernel frames include `kernel_init`, optional `rest_init`, `ret_from_fork`, and the panic path for killing init.

Control flow: PID 1 faults in `kernel_init`, the trace is short, and the kernel panics with `Attempted to kill init! exitcode=0x0000000b`. The parser must title from the exception plus RIP function and detect the panic tail.

State and persistence behavior: static boot/early-init crash fixture. It persists fatal process state through the panic line but has no mutable test state.

Dependencies and integration points: depends on Linux exception pattern matching for `stack segment`, RIP extraction, and panic detection. Integrates init-thread faults into report parser coverage.

Risks: short trace and absent syz-executor context can expose assumptions that crashes always occur in fuzzing tasks. The panic line should not replace the original stack-segment fault title.

Test signals: `stack segment: 0000 [#1]`, `RIP: kernel_init+0x55/0x122`, `ret_from_fork`, and `Kernel panic - not syncing: Attempted to kill init`.
