# File Research: sources/os/plan9/9front/sys/src/9/mt7688/trap.c

This file implements MT7688 trap, exception, and fault dispatch. It maps MIPS exception codes to names, has register-name metadata for dumps, diagnoses virtual coherence exceptions, and routes interrupts, TLB misses, watchpoints, coprocessor-unusable traps, and fatal kernel faults.

`trap(Ureg*)` enters kernel context, checks TLB shutdown, decodes the exception code, dispatches `CINT` through `intr`, TLB miss/modification through `kfault` or `faultmips`, watch exceptions through `fpwatch`, and COP1 unusable traps through `fpuemu`. User-mode unhandled traps become posted notes; kernel-mode unhandled traps dump registers/stack and exit.

After successful FP emulation it checks emulated FCR31 exception state and posts an FP note if enabled exceptions are pending. On user return it calls `donotify`, adjusts FP/user state comments, and exits kernel context.

Debug helpers include `fpexcname`, `callwithureg`, `dumpstack`, and `dumpregs`.

Filesystem relevance is direct through page faults and syscall-adjacent user exception handling. Any filesystem server faulting on mapped memory, copying buffers, or receiving notes relies on this path.

Notable risks: FP hardware exception path panics because there is no FPU; VCE handling is diagnostic-heavy; kernel faults in KSEG3 are treated as kmap faults and resolved through `kfault`.
