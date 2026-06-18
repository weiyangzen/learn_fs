# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/module.py

## Purpose
This module validates SELinux module names, creates standard reference-policy module directory trees, and wraps command-line compilation/packaging tools for `.te` policy modules.

## Important APIs, Types, And Functions
`is_valid_name(modname)` accepts names that start alphabetically and contain only letters, digits, underscore, hyphen, and period. `ModuleTree` derives canonical file paths for `.te`, `.fc`, `.if`, `.pp`, and `Makefile`, then `create()` makes a module directory, writes a Makefile include, and creates empty standard policy files. `modname_from_sourcename()` strips directory and extension.

`ModuleCompiler` wraps `/usr/bin/checkmodule`, `/usr/bin/semodule_package`, and `/usr/bin/make`. Important attributes include `mls`, `module`, `checkmodule`, `semodule_package`, `make`, `refpol_makefile`, `output`, and `last_output`. `create_module_package()` dispatches to `refpol_build()` for refpolicy builds or to `compile()` plus `package()` for direct builds. `gen_filenames()` maps a `.te` source to `.mod` and `.pp`.

## Control Flow
Directory creation is simple path derivation followed by `os.mkdir`, Makefile write, and empty file creation. Compilation flow builds shell command strings, runs them via `getstatusoutput`, records command/output through `o()`, and raises `RuntimeError` when commands return nonzero. Non-refpolicy builds delete the intermediate `.mod` after packaging.

## State And Persistence Behavior
`ModuleTree.create()` persists a new module subtree on disk. `ModuleCompiler` persists generated `.mod` and `.pp` files in the current working directory or source-relative command context and deletes only the intermediate `.mod` in direct mode. `last_output` stores the most recent command or command output for diagnostics.

## Dependencies And Integration Points
It depends on `selinux.is_selinux_mls_enabled()`, `defaults.refpolicy_makefile()`, filesystem modules, and external SELinux toolchain executables. Generated module trees are consumed by refpolicy build tooling and output produced by `policygen`/`output`.

## Risks And Edge Cases
Command strings are built by joining unquoted paths and source names, so spaces or shell metacharacters in paths can break or become unsafe if caller input is not trusted. `is_valid_name()` indexes `modname[0]` and fails on empty strings. `ModuleTree.create()` assumes parent directories exist and target module directories do not. `gen_filenames()` raises `RuntimeError` with an unused formatting argument pattern. Refpolicy build ignores `sourcename` and runs make against the configured Makefile only.

## Test Signals
Tests should validate allowed and rejected names, empty-name behavior, path derivation, file creation with custom/default Makefile includes, `.te` filename conversion with multiple periods, command construction for MLS/module flags, failure propagation, and cleanup of non-refpolicy `.mod` intermediates.
