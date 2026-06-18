# File Research: sources/virtualization/spdk/lib/env_dpdk/sigbus_handler.c

Provides a global SIGBUS dispatch mechanism for PCI error handlers.

Important behavior:
- Installs a `SIGBUS` `sigaction` handler at library constructor time.
- Maintains a mutex-protected tail queue of registered `spdk_pci_error_handler` callbacks.
- On SIGBUS, calls each registered callback with `info->si_addr` and the callback context.
- Prevents duplicate registration by function pointer.
- Frees handler records at destructor time.

Risk note: the signal handler locks a pthread mutex and calls arbitrary callbacks, which is not async-signal-safe in strict POSIX terms; this is an SPDK-specific fault-dispatch mechanism.
