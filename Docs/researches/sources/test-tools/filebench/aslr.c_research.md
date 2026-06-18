# sources/test-tools/filebench/aslr.c

## Purpose
`aslr.c` provides Filebench startup support for disabling per-process address space layout randomization where the platform allows it. Filebench uses fixed `MAP_FIXED` mappings across fork/exec, so ASLR can cause mappings to overlap unrelated regions and crash workloads.

## Important APIs, Types, and Functions
The platform-specific implementation is `linux_disable_aslr()` when both `HAVE_SYS_PERSONALITY_H` and `HAVE_ADDR_NO_RANDOMIZE` are defined. The fallback is `other_disable_aslr()`. Both log through `filebench_log()` and are selected by `aslr.h`.

## Control Flow and State
On Linux-capable builds, the function calls `personality(0xffffffff)` and then `personality(0xffffffff | ADDR_NO_RANDOMIZE)`, logging an error if the second call returns `-1`. On unsupported platforms, the fallback logs a manual sysctl instruction rather than changing process flags.

## Persistence and Dependencies
Persistent effect is process personality state for the current process and descendants after exec; fallback changes no state. Dependencies: `config.h`, `<sys/personality.h>` when available, Filebench logging (`filebench.h`), and `aslr.h` inline dispatch.

## Integration Points, Risks, and Test Signals
Integration is early Filebench process setup before fixed mappings are used. Risks include preserving current personality bits incorrectly if the first call result is ignored, Linux-only behavior, broad manual sysctl advice, and relying on compile-time feature detection. Test signals are no ASLR-related workload crashes and either absence of the error log or the informational unsupported-platform log.
