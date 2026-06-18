# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modsubr.c

## Purpose

`modsubr.c` provides support routines for the illumos module and driver binding subsystem. It maps driver names to major numbers, manages driver `dev_ops` holds, installs module call stubs, initializes `devnames`, tracks syscall names, parses driver `.conf` attachment data into parent/class lists, and indexes `.conf` child specs for nexus lookup.

Read completely: 1,154 lines.

## Main Responsibilities

- Validates and queries driver major-number state with `major_valid()`, `driver_installed()`, and `driver_active()`.
- Holds and releases loaded driver `dev_ops` by major number or `dev_info_t`, autoloading drivers when needed.
- Provides default `nomod_*` stub functions for absent modules.
- Installs, uninstalls, and resets module stubs through `install_stubs_by_name()`, `init_stubs()`, `install_stubs()`, `uninstall_stubs()`, and `reset_stubs()`.
- Maintains name-to-major and name-to-syscall binding hash tables.
- Initializes `devnamesp` from boot-time bindings and creates individual driver name slots.
- Parses and attaches `driver.conf` parent lists and global properties to `devnames`.
- Maintains hashed `.conf` child specs by parent name/path and exported class name.

## Key Data Structures And Globals

- `mb_hashtab`: driver/module name and alias to major-number hash.
- `sb_hashtab`: syscall name to syscall-number hash.
- `struct bind`: hash entry with key name, numeric binding, optional binding name, and deletion-by-negative-number state.
- `devnamesp`: global per-major driver metadata array populated by `init_devnamesp()` and `make_devname()`.
- `hwc_par_hash`: `.conf` child specs keyed by parent path, device name, binding name, or driver name.
- `hwc_class_hash`: `.conf` child specs keyed by exported hardware class.
- `hwc_hash_lock`: serializes insertion, removal, and lookup of `.conf` child spec hash state.

## Driver Holds And Stubs

`mod_hold_dev_by_major()` checks that a major number is active, locks the corresponding `devnames` entry, autoloads the driver if the installed `dev_ops` is still a placeholder, and increments the `dev_ops` reference count. `mod_rele_dev_by_major()` decrements that reference and panics on an unheld driver outside debug builds.

Stub installation resolves each module stub symbol name from the kernel symbol table, looks up the real function address in the loaded module, records it in `mod_stub_info`, and then marks stubs installed with producer memory barriers. Resetting stubs returns weak/nounload stubs to their error functions and ordinary stubs to `mod_hold_stub`.

## Binding Tables

`make_mbind()` inserts a `(name, number, bind_name)` entry after rejecting active duplicates. `delete_mbind()` and `purge_mbind()` keep entries in place but negate `b_num`, allowing debug detection of stale references to removed drivers. `mod_name_to_major()` returns only active matches, while `mod_major_to_name()` reads from `devnamesp`.

`init_devnamesp()` allocates the `devnames` array, transfers all active name-to-major bindings into it, warns on duplicate or invalid major numbers, and initializes `.conf` spec hash tables. `init_syscallnames()` similarly converts syscall bindings into the `syscallnames` array.

## Driver.conf Handling

`impl_make_parlist()` parses `drv/<driver>.conf` through `hwc_parse()`, installs global property lists, hashes every parsed `hwc_spec`, and sets per-driver flags such as force attach, interruptible open, SCSI size clean, pHCI driver, and devid registrant. `impl_free_parlist()` unreferences global properties, unhashes child specs, deletes the parent list, and clears parsed state.

`hwc_get_child_spec()` is the main nexus-facing lookup. For a parent `dip`, it searches from most specific to least specific:

- full device pathname,
- `nodename@address`,
- parent/binding form from `i_ddi_parname()`,
- binding name,
- driver name,
- exported classes.

It duplicates matching specs into a caller-owned list and can filter matches by child driver major.

## Locking And Ordering

- `devnamesp[major].dn_lock` protects driver `dev_ops`, per-major flags, parsed `.conf` lists, and global property pointers.
- `mod_lock` protects module-list search in `mod_getctl()`.
- `hwc_hash_lock` protects both parent and class `.conf` hash tables.
- Stub install/uninstall uses producer memory barriers around `MODS_INSTALLED` flag changes.
- Binding hash helpers are explicitly unsynchronized and intended for boot-time or externally locked use.

## Notable Edge Cases

- Removed bindings remain in hash chains with negative numbers for stale-reference diagnostics.
- `mod_rele_dev_by_major()` panics if a driver reference is released when not held.
- `make_devname()` rejects major numbers beyond `L_MAXMAJ32` and slots reserved by `getudev()`.
- `.conf` parent specs for unresolved absolute paths can remain discoverable for dynamic reconfiguration.
- `hwc_hash_remove()` may replace a hash head with the next spec while preserving the key.

## Research Relevance

This file is central to illumos device and storage discovery because it connects driver names, major numbers, `driver.conf` properties, and nexus-created child specs. Filesystem and block-device availability depend on this machinery to bind storage drivers and expose configured child devices.
