<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/modify_ldt02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/modify_ldt02.c

## Purpose
This file i386-only segment access regression that expects SIGSEGV after replacing an LDT entry with an invalid base.
The source-level description states or implies: Verify that after writing an invalid base address into a segment entry, a subsequent segment entry read will raise SIGSEV.

## Important APIs, Types, and Functions
Key local functions: `read_segment()`, `run()`.
LTP and helper APIs used include: `SAFE_FORK`, `SAFE_WAITPID`, `TST_EXP_EQ_LI`, `tst_res`, `tst_strstatus`, `tst_test`.
Harness fields present in `struct tst_test`: `.forks_child`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.

## State and Persistence
Persistent or externally visible state includes child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `modify_ldt` syscall test directory. x86/i386 LDT ABI via lapi/ldt.h and SAFE_MODIFY_LDT; tests are architecture-gated.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/modify_ldt02.c -->
