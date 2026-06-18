# File Research: sources/os/bsd/freebsd-src/sys/sys/pmckern.h

This header defines the interface used by the base kernel to call into the hwpmc module. It includes core kernel headers, `sys/pmc.h`, and machine CPU functions.

It assigns hook function numbers for process exec, context switch in/out, sample processing, mmap/munmap, user callchain capture, soft sampling, thread create/exit/userret, and thread/process logging. Small structs describe exec address changes, map-in/map-out events, and software PMC samples. `ring_type_t` distinguishes hardware, software, and userret sample rings.

The soft-PMC macros define and register dynamic software events at SYSINIT/SYSUNINIT time. `PMC_SOFT_CALL` and `PMC_SOFT_CALL_TF` conditionally invoke the hwpmc hook when a software event is running, disabling interrupts around trapframe setup/capture where required.

Global hook pointers (`pmc_hook`, `pmc_intr`), `pmc_sx`, per-CPU sampled flags, system-wide sampling count, kernel version, per-CPU trapframes, and per-domain log buffer headers are declared. Hook invocation macros support epoch-protected calls, exclusive-lock calls, and lock-free calls for context switch/clock paths. Helper macros detect active hooks, PMC-using processes, pending samples/callchains, active system sampling, and CPU sample availability. CPU availability and soft-event registration/acquire/release functions are declared.

Filesystem relevance is profiling integration: this is how exec, mmap, context switch, and sampling paths notify hwpmc so profiler output can be correlated with processes, mappings, and kernel activity.
