<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns.h

Purpose: Copyright (c) Linux Test Project, 2014-2020

Important APIs/types/functions: exposes shared helpers and declarations used by sibling `setns` tests. Visible symbols include functions `get_ns_fd`, `init_ns_type`, `init_available_ns`, `close_ns_fds`, structs none, arrays none, and helper macros/APIs `SAFE_CLOSE`, `SAFE_OPEN`, `tst_brk`, `tst_res`.

Control flow: this header has no standalone test entry point. Its inline helpers or declarations are compiled into the including test files, where setup and run callbacks drive them through the LTP harness.

State and persistence behavior: any state is owned by the caller. Header helpers in this shard mostly wrap temporary mappings, namespace descriptors, syscall variant tables, or memory accounting buffers and rely on the caller to allocate and free resources.

Dependencies and integration points: integrates sibling tests with LTP helper libraries, Linux UAPI wrappers, and architecture or libc variant abstractions. Include guards keep the declarations safe for repeated inclusion.

Risks: because the header centralizes shared ABI details, an incorrect prototype, syscall number selection, or cleanup helper can affect every sibling test. Inline helpers that map memory or open namespace files must preserve caller cleanup expectations.

Test signals: the header is validated indirectly when all including `setns` tests compile and their runtime assertions pass.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns.h -->
