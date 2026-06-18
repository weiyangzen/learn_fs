# File Research: sources/os/plan9/9front/sys/src/9/teg2/arch.c

Generic ARM/Tegra architecture glue for process and register handling. It supplies `setkernur`, `evenaddr`, `userpc`, `setregisters`, `kprocchild`, `dbgpc`, `procsetup`, `procsave`, `procfork`, `procrestore`, and `userureg`.

Most FP work delegates to VFP helpers. `procsave` writes back cache around the `Proc`, and `procrestore` wakes WFI and writes back L1 cache for stability. `setregisters` preserves PSR mode/interrupt bits when userland writes register state through `/proc`.
