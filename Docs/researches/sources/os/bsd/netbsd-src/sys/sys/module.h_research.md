# File Research: sources/os/bsd/netbsd-src/sys/sys/module.h

Defines NetBSD kernel module metadata, registration, runtime state, and `modctl` ABI. It declares module classes, sources, command types, `modinfo_t`, kernel `module_t` state, link-set or rump constructor registration machinery, the `MODULE` macro, module lists/globals, load/unload/autoload/builtin/specificdata/callback APIs, VFS loading hooks, module base/machine strings, and userland `modctl` load/stat structures.

It integrates with `kobj`, VFS loading, properties, sysctl cleanup, dependencies, and compatibility stubs. Risks are module dependency/refcount correctness, forced unload policy, built-in vs loadable registration differences, user pointer validation in `modctl_load_t`, and ABI stability of `modstat_t`.
