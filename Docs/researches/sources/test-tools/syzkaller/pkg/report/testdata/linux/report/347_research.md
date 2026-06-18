<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/347 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/347

## Purpose
This fixture tests XFRM warning selection when an earlier failslab/netdevice event trace precedes the actual warning. The expected result remains `WARNING in xfrm_state_fini`.

## Important APIs, Types, And Functions
The early stack includes `__should_failslab`, `kmem_cache_alloc_trace`, `netdevice_event`, notifier calls, ioctl syscall frames, and user RIP. The later root warning is `xfrm_state_fini` on workqueue `netns cleanup_net`.

## Control Flow
The parser must not stop at the first call trace. It needs to find the warning line, attach the following XFRM cleanup stack, and mark `PANICKED: Y` from panic-on-warn.

## State And Persistence
Persistent state is warning title/type/panic metadata. Runtime state includes injected allocation failures and namespace cleanup teardown.

## Dependencies And Integration Points
It depends on root-report selection amid pre-report traces, prefixed context handling, and workqueue stack extraction.

## Risks
An overly eager parser could use `netdevice_event` or `ioctl` as the title before reaching the warning.

## Test Signals
Stable output is `WARNING in xfrm_state_fini`, type `WARNING`, panicked.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/347 -->
