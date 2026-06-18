<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/338 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/338

## Purpose
This fixture verifies KASAN slab-out-of-bounds write parsing for module init code, normalizing from the immediate buggy helper to `do_one_initcall`. The expected title is `KASAN: slab-out-of-bounds Write in do_one_initcall`, alt `bad-access in do_one_initcall`, type `KASAN-WRITE`.

## Important APIs, Types, And Functions
Important markers include `BUG: KASAN: slab-out-of-bounds in kmalloc_oob_right`, `Write` access metadata, `__asan_report_store1_noabort`, `kmalloc_oob_right`, `kmalloc_tests_init`, `do_one_initcall`, `do_init_module`, `load_module`, and `__do_sys_init_module`.

## Control Flow
The parser consumes the KASAN report, recognizes a write, filters internal test-module helpers where appropriate, and chooses the stable initcall frame. It also handles allocation/free stack sections after the primary fault stack.

## State And Persistence
The fixture persists KASAN type and alt metadata. The raw log stores allocation provenance and module-loading state but no mutable repository state.

## Dependencies And Integration Points
It depends on KASAN read/write classification, bad-access alt generation, module suffix handling like `[test_kasan]`, and frame-priority logic that can select `do_one_initcall`.

## Risks
Parser changes might title the report as `kmalloc_oob_right` or `kmalloc_tests_init`, changing deduplication semantics.

## Test Signals
Expected output keeps title `KASAN: slab-out-of-bounds Write in do_one_initcall`, type `KASAN-WRITE`, and alt `bad-access in do_one_initcall`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/338 -->
