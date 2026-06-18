<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/352 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/352

## Purpose
This fixture validates kernel BUG parsing in the memory compaction allocator. The expected title is `kernel BUG in __isolate_free_page`, type `BUG`, panicked.

## Important APIs, Types, And Functions
The root marker is `kernel BUG at mm/page_alloc.c:3112!` with `RIP: __isolate_free_page+0x4a8/0x680`. The stack includes `compaction_alloc`, `migrate_pages`, `compact_zone`, `kcompactd_do_work`, and `kcompactd`. A later circular locking dependency report involving console locks is secondary.

## Control Flow
The parser must select the BUG/oops block first, derive the title from the RIP symbol, classify as `BUG`, and not let the following lockdep dependency report replace the root.

## State And Persistence
Persistent state is title/type/panic metadata. Runtime state includes kcompactd memory compaction, zone locks, console locks, and a following lockdep chain.

## Dependencies And Integration Points
It depends on kernel BUG pattern recognition, x86 invalid-op parsing, RIP function extraction, panic detection, and multi-report boundary handling.

## Risks
The secondary lockdep report is long and detailed, so boundary selection could mistakenly classify the fixture as lockdep rather than BUG.

## Test Signals
The stable parser result is `kernel BUG in __isolate_free_page`, `TYPE: BUG`, `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/352 -->
