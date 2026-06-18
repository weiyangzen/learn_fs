# File Research: sources/os/bsd/freebsd-src/sbin/geom/core/geom.c

## Purpose

Implements the generic GEOM userland command dispatcher. It loads class command definitions, parses command options, issues `gctl` requests, and provides standard `help`, `list`, `status`, `load`, `unload`, provider lookup, and topology tree views.

## Core Concepts

- `class_name`: lowercase class name, such as `part`.
- `gclass_name`: uppercase GEOM class name sent to kernel, such as `PART`.
- `class_commands`: command table loaded from a class library or static rescue class.
- `version`: class ABI/version pointer.
- `std_commands`: built-in generic commands available for all classes where supported.

## Command Flow

1. `main()` handles top-level `geom` options:
   - `-p provider`: list geom owning a provider.
   - `-t`: print GEOM topology tree.
   - `-h`: usage.
2. `get_class()` determines class from either `geom <class>` or a `g<class>` hardlink name.
3. `load_library()` dynamically loads `geom_<class>.so`, checks `G_LIB_VERSION`, and resolves `version` and `class_commands`.
4. `run_command()` finds a class command or standard command, optionally loads the kernel module, builds a `gctl_req`, parses options/arguments, invokes either a local command function or `gctl_issue()`, prints output, and exits.

## Option Parsing

- `parse_arguments()` builds a getopt string from `struct g_option`.
- Supports boolean, string, number, optional, and multi-value options.
- Numeric options use `expand_number()`.
- Parsed values are added to `gctl_req` as read-only params.
- Remaining positional arguments are passed as `arg0`, `arg1`, etc., plus `nargs`.

## Standard Commands

- `help`: usage.
- `list`: prints GEOM instances, providers, consumers, and config.
- `status`: tabular status by geom or provider, with script mode.
- `load`: loads kernel module if available.
- `unload`: unloads kernel module.

## Display Features

Uses `libxo` for structured output in list/status/provider modes. `show_tree()` computes column widths and recursively prints provider-consumer topology from roots.

## Integration Points

Uses `libgeom` for `geom_gettree()`, `geom_gettree_geom()`, `gctl_get_handle()`, `gctl_issue()`, and GEOM mesh structures. Uses kernel module APIs `modfind()`, `kldload()`, `kldfind()`, and `kldunload()`.

## Risk Notes

Class command metadata is trusted after ABI/version checks. `set_option()` stores allocated values inside option descriptors and request params for process lifetime. Standard-command availability can issue GEOM tree queries and kernel module path sysctls before a command runs.
