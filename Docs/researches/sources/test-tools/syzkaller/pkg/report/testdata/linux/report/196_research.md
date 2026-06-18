<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/196 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/196

## Purpose
This fixture extends report 195 with additional fault text after the initial KASAN SCSI generic read report. Expected title remains `KASAN: wild-memory-access Read in sg_read`, alt `bad-access in sg_read`, and type `KASAN-READ`.

## Important APIs, Types, And Functions
The file contains KASAN metadata and an 80-line mixed log. Important parser behaviors are first-report selection, handling of later `general protection fault`, and preservation of KASAN read classification. Important frames include `dump_stack`, `kasan_report`, `check_memory_region`, `kasan_check_read`, `__lock_acquire`, `_raw_write_lock_irqsave`, `sg_remove_request`, `sg_finish_rem_req`, `sg_read`, `do_readv_writev`, `vfs_readv`, `do_readv`, `SyS_readv`, and `entry_SYSCALL_64_fastpath`.

## Control Flow
The Linux reporter should detect the initial KASAN wild-memory access in `sg_read` and not let the later GPF/lock stack replace the primary title. Runtime flow remains readv into the SCSI generic driver, with request removal and lock acquisition appearing in the follow-on context.

## State And Persistence
The expected parser state is static in the headers. Dynamic addresses, lockdep data, and register dumps in the combined log are volatile. The source file is immutable test input.

## Dependencies And Integration Points
It depends on KASAN parsing, mixed-report boundary selection, and syzkaller title preference rules. It integrates with the Linux report test suite as a regression case for noisy logs.

## Risks
The primary risk is choosing the later `general protection fault` or `__lock_acquire` as the crash instead of the first KASAN report. Another risk is duplicate handling causing this fixture to diverge from report 195's expected title.

## Test Signals
Checks should assert the same title/alt/type as report 195 and verify that the parser's selected report is anchored to `BUG: KASAN: wild-memory-access in sg_read`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/196 -->
