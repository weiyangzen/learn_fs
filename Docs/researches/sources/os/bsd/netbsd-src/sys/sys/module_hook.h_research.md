# File Research: sources/os/bsd/netbsd-src/sys/sys/module_hook.h

Defines MP-safe module hook plumbing for vectored function calls whose implementation may live in unloadable modules. It uses a cacheline-aligned hook structure containing `localcount`, function pointer, and hooked flag, plus set/unset/call macros around `module_hook_tryenter` and `module_hook_exit`.

The design uses pserialize barriers during hook set/unset and localcount draining to prevent unload while calls are active. Risks are missing `MODULE_HOOK_UNSET` before unload, default-return correctness, function pointer lifetime, and always pairing successful tryenter with exit.
