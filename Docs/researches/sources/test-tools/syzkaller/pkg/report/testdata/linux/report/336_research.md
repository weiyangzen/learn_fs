<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/336 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/336

## Purpose
This fixture covers debugobjects/ODEBUG warning parsing from a corrupted and panicking log. The expected title is `WARNING: ODEBUG bug in corrupted`, type `WARNING`, corrupted and panicked.

## Important APIs, Types, And Functions
The leading marker is `ODEBUG: free active ... object type: timer_list hint: delayed_work_timer_fn`, followed by `WARNING` at `lib/debugobjects.c:287 debug_print_object`. Stack context includes socket allocation/sendmsg on one side and cleanup workqueue frames such as `kobject_delayed_cleanup`, `disk_release`, and `device_release`.

## Control Flow
The parser must prefer the ODEBUG warning class over later panic frames, then mark the report corrupted because multiple interleaved stacks and fault-injection context reduce reliable attribution.

## State And Persistence
The fixture persists the expected warning type plus corrupted/panicked flags. The runtime state includes active timer debug object state and panic-on-warn transition.

## Dependencies And Integration Points
It depends on ODEBUG-specific report patterns, generic warning parsing, panic detection, and report boundary logic for interleaved traces.

## Risks
Later cleanup stack frames can look like better function names; selecting them would lose the ODEBUG regression.

## Test Signals
The expected parse is `WARNING: ODEBUG bug in corrupted` with type `WARNING`, `CORRUPTED: Y`, and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/336 -->
