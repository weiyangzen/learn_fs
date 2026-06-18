# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modsysfile.c

## Purpose

`modsysfile.c` implements kernel parsers for early boot configuration files and driver metadata files. It reads `/etc/system` and `/etc/system.d/.self-assembly`, parses `driver.conf` files, alias/binding files, driver classes, DACF rules, optional PSM machine lists, and optional RTC configuration.

Read completely: 3,292 lines.

## Main Responsibilities

- Tokenizes kernel configuration files through `kobj_lex()`.
- Reads `/etc/system` commands into `sysparam` records.
- Applies `set`, `set32`, and `set64` assignments to kernel or module symbols.
- Applies early boot settings for `moddir`, root filesystem, swap device, and swap filesystem.
- Processes `forceload` and `exclude` directives.
- Parses `driver.conf` files into `.conf` child specs and global property lists.
- Parses `/etc/driver_aliases` and `/etc/ppt_aliases` into binding hashes.
- Parses generic binding files such as `/etc/name_to_major`, `/etc/name_to_sysnum`, and `/etc/path_to_inst`.
- Parses `/etc/dacf.conf` into DACF rules.
- Maintains driver class exports from `/etc/driver_classes`.

## Key Globals

- `systemfile`, `self_assembly`: early system configuration files.
- `versionfile`, `buildversion`: build-version string source and storage.
- `sysparam_hd`, `sysparam_tl`: parsed `/etc/system` command list.
- `mod_sysfile_arena`: vmem arena for parser-owned system parameter memory.
- `hcl_head`, `hcl_lock`: driver class list and lock.
- `obp_bootpath`: boot path storage.
- Optional `_PSM_MODULES` state for `/etc/mach`.
- Optional `_RTC_CONFIG` state for `/etc/rtc_config`.

## Lexer And /etc/system Parser

`kobj_lex()` recognizes punctuation, comments, strings, decimal and hexadecimal values, escaped names, unary numeric forms, whitespace, newlines, and EOF. `read_system_file()` consumes comments and one command per line, delegating command bodies to `do_sysfile_cmd()`.

Supported `/etc/system` command families include:

- `exclude`, `include`, `forceload`
- `rootdev`, `rootfs`, `swapdev`, `swapfs`
- `moddir`
- `set`, `set32`, `set64`

`include` is parsed but ignored. `set32` and `set64` are parsed for syntax but discarded on the opposite kernel data model. Duplicate logical entries are detected by `check_system_file()`, which also computes the final value for repeated `set` operations using assignment, bitwise AND, and bitwise OR semantics.

## Applying Settings

`mod_read_system_file()` creates the parser arena, optionally prompts for parameters, reads self-assembly first, then `/etc/system`, checks duplicates, runs parameter preset/check hooks, applies kernel variable assignments, optionally sets early boot parameters, and reads the build version file.

`mod_sysctl()` processes parsed commands for:

- `SYS_FORCELOAD`: loads modules and prevents autounload; driver paths also trigger `ddi_install_driver()`.
- `SYS_SET_KVAR` / `SYS_SET_MVAR`: writes parsed values into kernel or module symbols.
- `SYS_CHECK_EXCLUDE`: tests whether a module is excluded.

`sys_set_var()` uses ELF symbol lookup and writes 1-, 2-, 4-, or 8-byte integer values. Size-zero symbols are treated as `int` with a warning. `kobj_get_string()` stores string tokens in the parser arena, and `kobj_getvalue()` parses decimal, octal, hexadecimal, negated, and one's-complement numeric values.

## Driver.conf Parser

`hwc_parse()` is the public entry. Non-`t0` callers are handed to a double-stack helper thread to avoid deep-stack boot failures. `hwc_parse_now()` opens the `.conf` file through `kobj_open_path()`, tokenizes it, and parses entries with `get_hwc_spec()`.

`get_hwc_spec()` recognizes `parent`, `name`, `class`, and arbitrary properties. It builds a temporary `dev_info` to reuse DDI property creation helpers, then transfers the device name and system property list into an `hwc_spec`.

Property parsing supports:

- boolean properties with no value,
- integer arrays,
- string arrays,
- validation against reserved IEEE 1275 property-name characters,
- rejection of mixed value types.

`add_spec()` groups node specs into `par_list` records by parent major or class. `add_props()` preserves global property order. `impl_delete_par_list()` and `hwc_free_spec_list()` free parsed structures.

## Alias, Binding, Class, And DACF Files

`parse_aliases()` and `make_aliases()` read `/etc/ppt_aliases` and `/etc/driver_aliases`, resolve each driver name to a major number, and add alias bindings.

`read_binding_file()` is a generic parser for files with `name number [binding-name]` entries. It clears an existing hash, opens the file, invokes the supplied line parser for each complete entry, and returns the largest parsed number.

`read_class_file()` rebuilds `hcl_head` from `/etc/driver_classes`. `add_class()` validates that the exporter has a major number before linking a class export. `get_class()` returns class names for an exporter while the caller holds `hcl_lock`. `impl_parlist_to_major()` resolves parent lists into parent major-number sets, including class-to-exporter expansion.

`read_dacf_binding_file()` parses `/etc/dacf.conf`, clears the DACF rule database under `dacf_lock`, and registers rules of the form device-spec, optional module/opset, operation, options, and named config arguments.

## Optional Platform Parsers

Under `_PSM_MODULES`, `open_mach_list()`, `get_next_mach()`, and `close_mach_list()` maintain a simple list of platform-specific machine module names from `/etc/mach`.

Under `_RTC_CONFIG`, `process_rtc_config_file()` extracts only `zone_lag=<decimal>` from `/etc/rtc_config`, warning on malformed partial entries and ignoring unrelated configuration.

## Locking And Memory

- `/etc/system` parser allocations live in `mod_sysfile_arena`.
- Driver class list access is serialized by `hcl_lock`.
- DACF rule replacement is serialized by `dacf_lock`.
- `hwc_parse()` helper thread uses a semaphore to return parse completion to the caller.
- `driver.conf` property creation uses DDI property APIs on temporary devinfo state.

## Notable Edge Cases

- `hwc_parse_now()` returns success after opening a file even when individual lines are malformed; bad lines are skipped.
- Comments in DACF files are accepted only at the start of a line.
- `read_binding_file()` panics if a required binding file is missing.
- `mod_sysvar()` can fetch an early global or module-specific `set` value before module load.
- Duplicate `/etc/system` warnings report the final effective value, not merely the last token.
- Unresolved absolute `parent=` paths can be retained with major `(major_t)-2` for later dynamic reconfiguration.

## Research Relevance

This file defines how boot-time kernel configuration, driver aliases, `driver.conf` child nodes, and class metadata enter the kernel. It is directly relevant to filesystem and storage behavior because module loading, root/swap setup, block driver binding, and nexus child creation all depend on these parsed files.
