<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/343 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/343

## Purpose
This large fixture verifies KASAN stack-out-of-bounds read parsing in a heavily corrupted IPv6/GUE/UDP error path. The expected title is `KASAN: stack-out-of-bounds Read in __udp6_lib_err`, alt `bad-access in __udp6_lib_err`, type `KASAN-READ`, corrupted and panicked.

## Important APIs, Types, And Functions
The initial KASAN marker is `BUG: KASAN: stack-out-of-bounds in debug_lockdep_rcu_enabled.part.0`, with repeated recursive frames through `__udp6_lib_err`, `udpv6_err`, `gue6_err_proto_handler`, and `gue6_err`. Later corruption includes list-debug failures, usercopy/slab complaints, `__list_add_valid`, futex wakeup frames, circular-locking reports, and a final fatal exception panic.

## Control Flow
The parser must select the first KASAN report, then score the meaningful stack frame as `__udp6_lib_err` rather than internal helpers or later corrupted secondary failures. It also needs to mark corruption because task names, PIDs, stack pointers, list state, and follow-on reports are visibly damaged.

## State And Persistence
The file persists all expected metadata and a long raw log with repeated recursion and secondary crashes. Runtime state includes IPv6 tunnel error recursion, corrupted task identity, damaged lists, and final panic.

## Dependencies And Integration Points
This fixture exercises KASAN access-type parsing, bad-access alt generation, repeated frame handling, corruption detection, report-boundary selection, and panic-after-report detection.

## Risks
The biggest risk is selecting a later `kernel BUG`, lockdep circular dependency, or `__list_add_valid` crash instead of the initial KASAN report. The recursive stack can also cause unstable title frame ranking.

## Test Signals
Stable parsing keeps `KASAN: stack-out-of-bounds Read in __udp6_lib_err`, type `KASAN-READ`, alt `bad-access in __udp6_lib_err`, and both corrupted and panicked flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/343 -->
