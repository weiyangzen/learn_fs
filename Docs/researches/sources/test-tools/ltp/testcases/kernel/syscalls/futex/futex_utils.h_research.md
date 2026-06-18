<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_utils.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_utils.h

Purpose: Shared futex syscall-variant and process/thread state helpers for futex tests. Source notes: Wait for nr_threads to be sleeping skip ".", ".." and the main thread FUTEX_UTILS_H__ SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (76 lines, 1742 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_OPENDIR, SAFE_READDIR, SAFE_FILE_SCANF, SAFE_CLOSEDIR; types/structs: struct futex_test_variants, struct dirent; functions: futex_variant, wait_for_threads; local macros/constants: FUTEX_UTILS_H__, FUTEX_VARIANTS.

Control flow: the file provides declarations/helpers consumed by sibling tests; notable execution mechanics: runs across syscall ABI variants.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, futex words and scheduler-visible wait queues. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdio.h`, `stdlib.h`; integrates with the LTP futex syscall suite.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: key constants: FUTEX_UTILS_H__, __NR_futex, __NR_futex_time64, FUTEX_VARIANTS, FUTEX_FN_FUTEX, FUTEX_FN_FUTEX64.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_utils.h -->
