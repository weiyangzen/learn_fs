# sources/test-tools/syzkaller/sys/windows/init.go

Purpose: initializes Windows target memory mapping via `VirtualAlloc`.

Important APIs/types/functions: `InitTarget`, `arch`, and `arch.makeMmap`.

Control flow: `InitTarget` captures `VirtualAlloc` syscall metadata and memory/protection constants, then assigns `MakeDataMmap`. `makeMmap` builds a single `VirtualAlloc` call over the target data VMA with `MEM_COMMIT|MEM_RESERVE` and `PAGE_EXECUTE_READWRITE`.

State and persistence: no durable state; creates in-memory setup calls.

Dependencies and integration points: depends on Windows syzlang exposing `VirtualAlloc` and constants; consumed by generated target registration.

Risks: no neutralizer is installed. Page-size TODO in target config means mapping assumptions may need revision for Windows allocation granularity.

Test signals: no direct tests here.
