# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/623

## Purpose
This fixture is another memfd secret refcount warning, but its canonical title is `WARNING: refcount bug in sys_memfd_secret`.

## Important APIs, types, and functions
Important frames include `refcount_warn_saturate`, `__x64_sys_memfd_secret`, `do_syscall_64`, and `entry_SYSCALL_64_after_hwframe`.

## Control flow
The syscall path enters the x86-64 wrapper and triggers the same `refcount_t: addition on 0; use-after-free` diagnostic.

## State and persistence behavior
The fixture keeps the wrapper-specific expected title and an alternate for `__x64_sys_memfd_secret`.

## Dependencies and integration points
It complements report 622 and verifies architecture-specific syscall wrapper handling in syzkaller report tests.

## Risks and test signals
The risk is over-normalizing this report to `memfd_secret`. Passing behavior preserves `sys_memfd_secret` as the title target.
