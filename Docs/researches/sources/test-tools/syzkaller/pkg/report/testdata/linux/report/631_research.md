# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/631

## Purpose
This fixture covers a memory-safety bug titled `BUG: unable to handle kernel paging request in __unwind_start`.

## Important APIs, types, and functions
Important frames include `__read_once_word_nocheck`, `__unwind_start`, stack unwinding code, and syscall return frames. The expected type is `MEMORY_SAFETY_BUG`.

## Control flow
A page fault occurs while the kernel is reading stack words for unwinding. The raw faulting instruction is a low-level read helper, but the useful subsystem frame is `__unwind_start`.

## State and persistence behavior
The fixture persists fault address, page-fault diagnostic data, registers, and expected metadata.

## Dependencies and integration points
It exercises page-fault report parsing and frame selection in the kernel unwinder.

## Risks and test signals
The parser must normalize the report to `bad-access in __unwind_start` as an alternate and classify it as memory safety.
