<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/346 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/346

## Purpose
This is a second XFRM cleanup warning fixture for `xfrm_state_fini`, preserving parser stability across slightly different interleaving and prefix formats.

## Important APIs, Types, And Functions
The significant marker is the warning at `net/xfrm/xfrm_state.c:2381 xfrm_state_fini+0x440/0x5c0`, with stack frames `xfrm_net_exit`, `ops_exit_list.isra.0`, `cleanup_net`, and workqueue execution.

## Control Flow
The reporter scans past earlier noise, selects the warning block, derives the title from `xfrm_state_fini`, and marks panic-on-warn.

## State And Persistence
The header persists `TITLE: WARNING in xfrm_state_fini`, `TYPE: WARNING`, and `PANICKED: Y`. The body stores raw kernel timing and task context.

## Dependencies And Integration Points
It integrates with Linux warning parsing, XFRM symbol extraction, prefixed printk cleanup, and panic detection.

## Risks
The similarity to reports 345, 347, and 348 means deduplication-sensitive changes must keep identical titles for equivalent crashes.

## Test Signals
The test signal is identical warning title/type/panic metadata for this input variant.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/346 -->
