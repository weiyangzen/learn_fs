<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg_var.h

Purpose: Header support for the LTP `sendmmsg` syscall tests.

Important APIs/types/functions: exposes shared helpers and declarations used by sibling `sendmmsg` tests. Visible symbols include functions none, structs none, arrays none, and helper macros/APIs `sendmmsg`, `tst_brk`, `tst_syscall`, `tst_timer`.

Control flow: this header has no standalone test entry point. Its inline helpers or declarations are compiled into the including test files, where setup and run callbacks drive them through the LTP harness.

State and persistence behavior: any state is owned by the caller. Header helpers in this shard mostly wrap temporary mappings, namespace descriptors, syscall variant tables, or memory accounting buffers and rely on the caller to allocate and free resources.

Dependencies and integration points: integrates sibling tests with LTP helper libraries, Linux UAPI wrappers, and architecture or libc variant abstractions. Include guards keep the declarations safe for repeated inclusion.

Risks: because the header centralizes shared ABI details, an incorrect prototype, syscall number selection, or cleanup helper can affect every sibling test. Inline helpers that map memory or open namespace files must preserve caller cleanup expectations.

Test signals: the header is validated indirectly when all including `sendmmsg` tests compile and their runtime assertions pass.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg_var.h -->
