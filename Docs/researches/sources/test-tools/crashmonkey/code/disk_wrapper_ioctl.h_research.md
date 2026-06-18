# sources/test-tools/crashmonkey/code/disk_wrapper_ioctl.h

Purpose: defines the shared ioctl ABI and stable CrashMonkey flag encoding used by the kernel wrapper, cow RAM block device controls, and user-space harness/tests.

Important APIs/types: `HWM_LOG_OFF`, `HWM_LOG_ON`, `HWM_GET_LOG_META`, `HWM_GET_LOG_DATA`, `HWM_NEXT_ENT`, `HWM_CLR_LOG`, and `HWM_CHECKPOINT` are the wrapper commands. `COW_BRD_SNAPSHOT`, `COW_BRD_UNSNAPSHOT`, `COW_BRD_RESTORE_SNAPSHOT`, and `COW_BRD_WIPE` are cow_brd commands. `enum flag_shifts` defines a kernel-version-independent bit namespace for request semantics such as write, FUA, flush, discard, metadata, no-idle, integrity, and write-zeroes. `struct disk_write_op_meta` is the fixed metadata transferred to user space.

Control flow and integration: kernel code fills `disk_write_op_meta` for every logged write/checkpoint, and user-space code reads the structure before requesting the matching payload. Harness utilities construct `disk_write`/`DiskWriteData` objects from this metadata for serialization, replay, and permutation.

State and persistence behavior: this header does not store state, but it defines the interpretation of persisted profile logs saved by `Tester::log_profile_save()`. ABI changes here can make existing binary logs unreadable or semantically wrong.

Dependencies: included from kernel C code and user-space C/C++ code, so the definitions avoid Linux-only types in exported structures. It assumes `unsigned long` and `unsigned int` sizes are compatible between producer and consumer on the tested platform.

Risks: ioctl command numbers overlap (`HWM_CHECKPOINT` and `COW_BRD_SNAPSHOT` are both `0xff06`) and are not encoded with `_IO`, `_IOR`, or `_IOW`, so type checking and namespace separation are weak. The header lacks currently referenced stale commands such as `HWM_GET_LOG_ENT_SIZE` and `HWM_GET_LOG_ENT`, making older tests fail to compile. `disk_write_op_meta` uses architecture-sized `unsigned long` for sectors, which is less portable than fixed-width types.

Test signals: compile-time compatibility across kernel/user code is the first signal. Runtime signals come from successful log extraction in `Tester::get_wrapper_log()` and cow_brd snapshot operations in `Tester::clone_device()`.
