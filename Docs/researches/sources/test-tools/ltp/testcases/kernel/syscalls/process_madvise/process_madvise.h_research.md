<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise.h

Purpose: Shared wrapper header for process_madvise tests; it provides raw syscall access and feature detection for kernels/libc without a native wrapper.

Important APIs/types/functions: includes `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `tst_safe_stdio.h`; defines `read_address_mapping`; uses constants/macros such as `SAFE_FCLOSE`, `SAFE_FOPEN`.

Control flow: this file is consumed at compile time by sibling tests; any inline or fallback functions normalize missing libc/kernel interfaces before the test bodies run.

State and persistence behavior: Runtime state is a remote process address space referenced through pidfd plus iovec ranges and advice values passed to `process_madvise()`.

Dependencies and integration points: integrates with the LTP test framework, lapi syscall wrappers, and local syscall test sources. Direct include dependencies include `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `tst_safe_stdio.h`.

Risks and test signals: fallback wrappers must match the real syscall ABI exactly; otherwise sibling tests can pass compile but exercise the wrong argument layout. Signals are compile success and correct behavior in the consuming tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise.h -->
