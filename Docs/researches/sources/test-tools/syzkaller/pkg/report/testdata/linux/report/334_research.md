<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/334 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/334

## Purpose
This corrupted-stack-end fixture verifies title stability in the presence of an interleaved OOM-killer line. The expected root remains writeback stack overflow in `wb_workfn`.

## Important APIs, Types, And Functions
Important frames and markers are `Kernel panic - not syncing`, workqueue `writeback wb_workfn`, interrupted RIP `__add_to_page_cache_locked`, an OOM-killer message, and ext4/writeback frames ending at `wb_workfn`.

## Control Flow
The parser scans the panic, ignores the OOM status line as noise, and derives the title from the writeback worker context. It must not treat the OOM line as a separate report.

## State And Persistence
The fixture persists panicked `DoS` metadata and raw console noise around memory pressure. No mutable state exists outside the checked-in sample.

## Dependencies And Integration Points
It integrates with panic parsing, stack-overflow alternative generation, OOM-message filtering, and workqueue-aware frame selection.

## Risks
Interleaving can cause report-boundary or title contamination if OOM messages are not recognized as incidental.

## Test Signals
The expected parser signal is unchanged `wb_workfn` title/alt with `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/334 -->
