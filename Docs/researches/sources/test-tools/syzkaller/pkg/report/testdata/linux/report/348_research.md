<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/348 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/348

## Purpose
This is another XFRM cleanup warning variant, using CPU context prefixes like `[ C1]` rather than normal task prefixes. It verifies prefix normalization.

## Important APIs, Types, And Functions
Important markers are the prelude allocation/failslab call trace and the warning at `xfrm_state_fini+0x440/0x5c0`, followed by `xfrm_net_exit`, `ops_exit_list.isra.0`, `cleanup_net`, and worker frames.

## Control Flow
The parser strips or normalizes CPU prefixes, skips pre-warning noise, selects the XFRM warning, and records the panic-on-warn state.

## State And Persistence
The fixture persists expected title/type/panic state. The raw body preserves the unusual CPU-only printk prefix format.

## Dependencies And Integration Points
It depends on printk prefix parsing, warning extraction, workqueue cleanup stack handling, and panic detection.

## Risks
Prefix changes can cause the Linux reporter to miss stack frames or report boundaries.

## Test Signals
Expected output remains `WARNING in xfrm_state_fini`, `TYPE: WARNING`, `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/348 -->
