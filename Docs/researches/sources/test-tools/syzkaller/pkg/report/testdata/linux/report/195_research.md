<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/195 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/195

## Purpose
This fixture tests KASAN wild-memory-access read parsing in the SCSI generic read path. Expected title is `KASAN: wild-memory-access Read in sg_read`, alt `bad-access in sg_read`, type `KASAN-READ`.

## Important APIs, Types, And Functions
The fixture provides KASAN report data with headers and a 42-line stack. Parser features under test include KASAN read/write classification, function-title extraction, alternate bad-access title generation, and report boundary handling for short sanitizer traces. Important frames include `dump_stack`, `kasan_report`, `check_memory_region`, `kasan_check_read`, `sg_read`, `do_loop_readv_writev.part.17`, `do_readv_writev`, `vfs_readv`, `do_readv`, `SyS_readv`, and `entry_SYSCALL_64_fastpath`.

## Control Flow
The reporter finds `BUG: KASAN: wild-memory-access in sg_read` and selects `sg_read` as the function title. The runtime path is a user `readv` syscall through VFS into the SCSI generic driver.

## State And Persistence
Static state is the expected metadata and short raw KASAN report. The bad address, register state, and syscall arguments are volatile. No repository state changes occur.

## Dependencies And Integration Points
It depends on Linux KASAN regexes, SCSI generic stack frame extraction, and syzkaller's crash type mapping. It integrates as a standard report test fixture.

## Risks
The parser may return a generic wild-memory title without `sg_read`, or classify the report as `MEMORY_SAFETY_BUG` instead of `KASAN-READ`. Sanitizer helper frames must be skipped for title selection.

## Test Signals
Exact title, alt, and `KASAN-READ` type are required. The selected report should include the `sg_read` frame and readv syscall tail.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/195 -->
