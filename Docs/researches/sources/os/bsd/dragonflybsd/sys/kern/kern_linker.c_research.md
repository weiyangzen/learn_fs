# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_linker.c

## Purpose

`kern_linker.c` implements DragonFlyBSD's machine-independent kernel linker and KLD loader framework. It tracks loaded linker files, linker classes, module version providers, dependencies, sysinit/sysuninit execution, sysctl registration, symbol lookup, preloaded modules, disk search paths, and KLD-related syscalls.

## Main Responsibilities

- Initializes linker class and loaded-file lists.
- Registers linker classes with file-format-specific operations.
- Creates, finds, references, and unloads `linker_file` objects.
- Registers module metadata and sysctl sets found in linker files.
- Runs per-file `sysinit_set` in sorted order and `sysuninit_set` in reverse order.
- Resolves symbols from a file, its dependencies, and global loaded files.
- Allocates storage for unresolved common symbols.
- Implements `kldload`, `kldunload`, `kldfind`, `kldnext`, `kldstat`, `kldfirstmod`, and `kldsym`.
- Processes loader-preloaded files and resolves their dependency order.
- Searches `kern.module_path` for modules and loads dependencies for userland-initiated loads.

## Core Data Model

`classes` is the list of registered linker backends. `linker_files` is the global list of loaded linker files, protected by `llf_lock`. `kld_lock` serializes high-level KLD load/unload syscalls and is recursive. Each `linker_file` tracks filename, pathname, ID, refs, userrefs, flags, dependencies, common symbols, private backend state, modules, and backend ops.

`found_modules` maps provided module/interface names plus versions to the containing linker file. Despite the name, these entries represent version-provider tags from module metadata.

## Load and Unload Flow

`linker_load_file()` refuses loads when `securelevel > 0` or `kernel_mem_readonly` is set. If a file is already loaded, it increments `refs`; otherwise it asks each linker class to load the path. On success it registers modules, sysctls, runs sysinit functions, marks the file linked, and returns it.

`linker_file_unload()` refuses unloads under the same securelevel/read-only policy. It drops extra references cheaply. On final unload it lets each contained module veto via `MOD_UNLOAD`, removes provided-module records, runs SYSUNINITs and unregisters sysctls for linked files, unloads dependencies, frees common symbols, invokes backend unload, and removes the file from the global list.

## Symbol and Metadata Handling

`linker_file_lookup_symbol()` first queries the file backend. If a symbol looks like a common symbol, it records its size and searches dependencies and globals before allocating zeroed common storage in the file. DDB helpers provide unlocked cross-file symbol lookup and nearest-symbol search.

Module metadata is discovered from `modmetadata_set`/`MDT_SETNAME`. `linker_file_register_modules()` registers `MDT_MODULE` entries with the module subsystem. `linker_addmodules()` records `MDT_VERSION` providers in `found_modules`, and dependency checks use `MDT_DEPEND` plus `struct mod_depend` version bounds.

## Preload and Dependency Handling

`linker_preload()` scans loader metadata, asks linker classes to create preloaded files, records providers from the static kernel, then repeatedly moves preloaded files whose dependencies are satisfied into a dependency-ordered list. Unresolved files are unloaded. Resolved files depend on the kernel and on provider containers, run backend `preload_finish()`, register modules, add SYSINITs through `sysinit_add()`, register sysctls, and become linked.

`linker_load_dependencies()` handles userland KLD loads. It adds an implicit kernel dependency, rejects provider/version duplicates, resolves dependencies from already loaded providers or by loading missing modules, and finally records the new file's provided interfaces.

## User Interface and Security

KLD syscalls use `caps_priv_check_self(SYSCAP_NOKLD)` for load/unload, validate user structure versions, and copy names/pathnames/results to userland. `kern.module_path` is a semicolon-separated search path with `.ko` fallback. Loads and unloads are blocked once securelevel is raised or kernel memory is read-only.
