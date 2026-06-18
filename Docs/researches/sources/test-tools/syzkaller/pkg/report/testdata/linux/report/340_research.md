<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/340 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/340

## Purpose
This is a KASAN slab-out-of-bounds write fixture similar to report 338, but with an interleaved CPU context line around `kfree`. It verifies robust stack parsing under mixed printk prefixes.

## Important APIs, Types, And Functions
Key markers include `BUG: KASAN: slab-out-of-bounds in memcpy`, the call chain through `kmalloc_oob_right`, `kmalloc_tests_init`, `do_one_initcall`, module load frames, and an interleaved `[ C3] kfree` line.

## Control Flow
The parser must preserve the KASAN write report, ignore the interleaved CPU-only line as noise, and still choose `do_one_initcall` for the expected title and bad-access alt.

## State And Persistence
Persistent state is title/alt/type metadata. The raw log preserves module init state, KASAN allocation metadata, and mixed context prefixes.

## Dependencies And Integration Points
It integrates with KASAN write classification, prefix stripping for `[ T...]` and `[ C...]` contexts, and frame-priority logic for module init reports.

## Risks
Interleaved lines can break stack continuity or cause false selection of `kfree`/`memcpy`.

## Test Signals
The expected output is `KASAN: slab-out-of-bounds Write in do_one_initcall`, alt `bad-access in do_one_initcall`, type `KASAN-WRITE`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/340 -->
