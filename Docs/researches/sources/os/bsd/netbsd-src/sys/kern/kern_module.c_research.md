# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_module.c

## Purpose
Implements NetBSD kernel module management: initialization, built-in module registration, runtime load/autoload/unload, dependency recursion, bootloader-pushed modules, module metadata lookup, sysctl controls, autounload thread, module-specific storage, and load/unload callbacks.

## Main Interfaces
- `module_init`, `module_start_unload_thread`: initialize module lists, paths, kauth listener, sysctls, built-in module link-set entries, specificdata domain, and autounload thread.
- `module_builtin_add`, `module_builtin_remove`, `module_init_class`, `module_builtin_require_force`: manage built-in modules and class-based initialization.
- `module_load`, `module_autoload`, `module_unload`: public load/autoload/unload entry points with authorization and `kernconfig_lock` serialization.
- `module_hold`, `module_rele`, `module_lookup`, `module_kernel`, `module_name`, `module_source`.
- `module_prime`: registers a module image supplied by the bootloader.
- `module_find_section`: lets the currently initializing module query its ELF sections.
- `module_specific_key_create/delete`, `module_getspecific`, `module_setspecific`.
- `module_register_callbacks`, `module_unregister_callbacks`: callback hooks around existing and future module load/unload.

## Internal State And Dependencies
- Uses global module lists: `module_list`, `module_builtins`, `module_bootlist`, and callback list `modcblist`.
- `module_netbsd` is a synthetic module representing the kernel.
- `module_base` is initialized from booted kernel path or legacy `/stand/.../modules`.
- `module_load_vfs_vec` is an indirect VFS loading hook, initialized elsewhere by `kern_module_vfs.c`.
- Depends on `kobj` for ELF object load/affix/unload/section lookup, proplib dictionaries for module properties, kauth for authorization, sysctl, evcnt, specificdata, UVM memory pressure checks, and kthreads.

## Control Flow Notes
- `module_do_load` is the core loader. It handles built-ins, bootlist modules, filesystem modules, metadata validation, version/class checks, circular dependency detection, recursive dependency loading, `kobj_affix`, property merge, sysctl/evcnt setup, `MODULE_CMD_INIT`, queue insertion, autounload scheduling, and callbacks.
- Dependency recursion uses a stack of pending lists to detect circular dependencies and share pending state across nested dependency loads.
- `module_do_builtin` recursively initializes built-in prerequisites and moves successful built-ins from `module_builtins` to `module_list`.
- `module_do_unload` rejects referenced modules, prevents unloading built-in secmodels, calls unload callbacks and `MODULE_CMD_FINI`, tears down sysctls/evcnts, decrements dependency refs, unloads kobj, and either returns built-ins to the disabled list or frees filesystem modules.
- Autoload rejects names containing `/`, `@`, or `.` and can be disabled by sysctl.
- The autounload thread checks memory pressure or `module_autotime`, asks modules via `MODULE_CMD_AUTOUNLOAD`, and unloads audited or optionally unsafe modules.

## Locking And Correctness
- Most module list and lifecycle operations require `kernconfig_lock`.
- `module_active` tracks the module currently running init/fini for `module_find_section`.
- Module dependency references are incremented on enqueue and decremented on unload.
- Callback registration invokes load callbacks for existing modules under the config lock; unregistration invokes unload callbacks before removal.

## Risk Areas
- Loader failure paths must unwind kobj, pending list, file dictionaries, sysctl log, evcnt attachments, and dependency arrays in the right order.
- Built-in failure recovery is limited; class initialization moves failed built-ins aside and restores them after the pass.
- `module_active` is global and assumes serialized module init/fini.
- Autounload can unload only modules that cooperate or are allowed by unsafe policy.
- Duplicate module names can arise from filename/modinfo mismatch or recursive loads and are explicitly checked.

## Filesystem Relevance
High indirect relevance. Runtime module loading depends on VFS object/plist loading through `module_load_vfs_vec`, and filesystem drivers may be modules managed by this subsystem.
