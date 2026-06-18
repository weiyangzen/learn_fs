# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_linker.c

## Purpose
Implements the FreeBSD kernel linker/KLD manager: class registration, module load/unload, preload finalization, dependency resolution, sysinit/sysuninit execution, sysctl registration, symbol lookup, CTF loading, and user syscalls such as `kldload`, `kldunload`, `kldfind`, `kldnext`, `kldstat`, `kldfirstmod`, and `kldsym`.

## Key Interfaces
- Linker class and file lifecycle: `linker_add_class()`, `linker_make_file()`, `linker_file_unload()`, `linker_load_dependencies()`.
- Module ref APIs: `linker_reference_module()` and `linker_release_module()`.
- Symbol APIs: `linker_file_lookup_symbol()`, DDB helpers, and `linker_search_symbol_name[_flags]()`.
- KLD syscalls: `kern_kldload()`, `sys_kldload()`, `kern_kldunload()`, `sys_kldunload[f]()`, `sys_kldfind()`, `sys_kldnext()`, `sys_kldstat()`, `sys_kldfirstmod()`, `sys_kldsym()`.
- Function-name export sysctl: `kern.function_list`.

## State And Locking
Global linker state is guarded by `kld_sx`: classes, loaded files, ids, found module/version records, dependencies, load counter, and `kld_busy` serialization. File objects track refs, userrefs, flags, modules, dependencies, common symbols, load count, paths, address, size, and class-specific operations.

## Control Flow
Runtime load checks privilege and securelevel, serializes through `linker_kldload_busy()`, resolves a path or module name through `linker.hints` and `module_path`, invokes class-specific loading, registers module metadata and sysctls, propagates vnets, runs SYSINITs, loads CTF, and fires kld eventhandlers. Unload quiesces modules, runs module unload callbacks, unregisters sysctls, runs SYSUNINITs, releases dependencies, frees common symbols, and deletes the linker object.

## Integration Notes
Preload support scans loader metadata, topologically orders dependencies, finalizes relocation, registers sysinits and modules, and later assigns userrefs for unloadable preloaded files. Symbol lookup supports commons and the special `__this_linker_file` symbol used by LinuxKPI.

## Risks
Loading is disabled above securelevel 0. DDB lookup intentionally avoids normal locking. Hints parsing trusts bounded file size but still manually walks packed records. Dependency/version handling rejects duplicate or incompatible module versions and may force-unload partially linked files.
