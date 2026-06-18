# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/458

Purpose: golden fixture for an input-device teardown GPF where expected title is `general protection fault in input_close_device`, alternate title is `bad-access in input_close_device`, type is `DoS`, and `PANICKED: Y`.

Important APIs, types, and functions: parser coverage includes GPF parsing, bad-access alternate generation, and panic recognition. Kernel frames include `timer_is_static_object`, `debug_object_assert_init`, `del_timer`, `try_to_grab_pending`, `input_close_device`-related teardown, and userspace return frames.

Control flow: the immediate RIP is inside debugobjects/timer validation, with a call trace that flows through timer deletion and pending-work handling during input close. The parser's guilty-frame logic is expected to title the report as `input_close_device` rather than `timer_is_static_object`.

State and persistence behavior: static fixture persists fatal-exception panic state and repeated RIP/register output. No mutable runtime state is represented beyond the freed/uninitialized object implied by debugobjects.

Dependencies and integration points: depends on GPF/oops patterns, guilty-frame ranking that ignores generic debugobject helpers, and panic detection. Integrates input subsystem close paths and timer debug checks into report tests.

Risks: top-frame title selection would produce a generic debugobject function. The expected input-subsystem title relies on source/stack heuristics that may change as kernel internals evolve.

Test signals: `general protection fault: 0000 [#1] SMP KASAN`, `RIP: timer_is_static_object`, `debug_object_assert_init`, `del_timer`, `try_to_grab_pending`, and fatal-exception panic.
