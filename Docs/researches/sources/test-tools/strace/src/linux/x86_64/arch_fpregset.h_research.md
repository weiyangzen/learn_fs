<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_fpregset.h -->
# sources/test-tools/strace/src/linux/x86_64/arch_fpregset.h

Purpose: defines the native x86_64 floating-point regset layout used by `arch_fpregset.c`.
Important APIs/types/functions: `struct_fpregset` fields for x87 control/status, instruction/data pointers, MXCSR, x87 stack space, XMM space, and padding; `HAVE_ARCH_FPREGSET` feature macro.
Control flow: preprocessor selects i386 layout under `MPERS_IS_m32`, otherwise guards the local definition. State and persistence behavior: type declarations only.
Dependencies and integration points: consumed by regset decoders and ptrace output. Risks: layout drift relative to kernel/user headers corrupts printed offsets. Test signals: compile-time size checks and regset decoding tests across native and m32 builds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_fpregset.h -->
