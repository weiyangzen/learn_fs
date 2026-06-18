# File Research: sources/os/bsd/netbsd-src/sys/sys/ipi.h

Kernel-only interprocessor interrupt API. It defines asynchronous handler function type `ipi_func_t`, synchronous message structure `ipi_msg_t`, registration limit constants, bitset sizing macros, initialization hooks, CPU handler hooks, and public async/sync trigger APIs.

It depends on kernel CPU and `kcpuset_t` concepts supplied by surrounding includes. The key contracts are registration lifetime, `_pending` synchronization, broadcast/self behavior, and CPU set correctness. It is not exposed to userland except `_KMEMUSER` inspection.
