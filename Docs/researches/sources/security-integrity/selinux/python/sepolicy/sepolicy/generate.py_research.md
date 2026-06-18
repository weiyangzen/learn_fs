# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/generate.py

## Purpose
`generate.py` implements `policygentool`-style SELinux policy module generation. It collects requested application/user policy options, discovers host policy, ports, RPM ownership, writable paths, init scripts, and ELF symbol hints, then renders `.te`, `.if`, `.fc`, `.spec`, and setup shell script output from template modules under `sepolicy.templates`.

## Important APIs and types
Top-level helpers include `get_rpm_nvr_from_header()`, `get_rpm_nvr_list()`, `get_all_ports()`, `get_all_users()`, `get_poltype_desc()`, and `verify_ports()`. Constants define generated policy categories: daemons, DBus daemons, inetd services, CGI scripts, sandbox modules, application domains, existing domains, login user roles, root/admin roles, and new types.

The central type is class `policy`. Its constructor validates the module name/type, initializes host policy data (`get_all_roles()`, `get_all_ports()`), defines symbol-to-action heuristics, default path buckets and template modules, type-specific generator dispatch, and mutable generation state such as capabilities, process permissions, network flags, booleans, custom files/dirs, admin/transition domains, users, roles, and program/init script paths.

Public setters include `set_program()`, `set_init_script()`, `set_in_tcp()`, `set_in_udp()`, `set_out_tcp()`, `set_out_udp()`, feature toggles for resolver/syslog/Kerberos/PAM/DBus/audit/etc/localization/fd/terminal/mail/tmp/UID, and collection mutators for capabilities, processes, booleans, files, dirs, admin domains, existing domains, transition domains/users, roles, and new types.

## Control flow
Generation is staged. Inputs populate instance state; `gen_writeable()` and `gen_symbols()` can infer additional state from the host package database, filesystem, init script locations, and `nm -D` output. Type-specific methods render base type declarations and rules. Cross-cutting methods render capabilities, process permissions, network types/rules, file-context records, booleans, user/role transitions, admin rules, DBus/sandbox/admin interfaces, package specs, and setup scripts.

`generate_te()` is the main type-enforcement assembler: it emits default type declarations, selected default-directory types, a local policy marker for most module types, optional capability/process/network/tmp/boolean/default rules, per-directory template rules, and feature-specific rules. `generate_if()`, `generate_fc()`, `generate_sh()`, and `generate_spec()` assemble the other artifacts. `generate(out_dir)` writes files by calling `write_te()`, `write_if()`, `write_fc()`, and, except for `NEWTYPE`, `write_spec()` and `write_sh()`.

## State and persistence
Instance state is long-lived and accumulates user options and discovered resources. Output persistence is direct file creation in `out_dir`; generated setup scripts are chmodded `0750`. Host-state reads include SELinux policy data, active ports, RPM database, DNF/libdnf package metadata, filesystem paths under `/var`, `/etc/rc.d/init.d`, and dynamic symbols from the executable. The module does not apply policy itself; it emits artifacts and scripts.

## Dependencies and integration points
Dependencies include `sepolicy`, selected `sepolicy` query functions, libselinux indirectly, `sepolgen.interfaces/defaults`, many `sepolicy.templates` modules, optional `rpm`, optional `libdnf5` or `dnf`, `nm`, `grep`, and filesystem metadata via `os`/`stat`. It integrates with CLI front ends that gather user choices and with RPM packaging workflows through generated spec/setup scripts.

## Risks and edge cases
The code has Python 3 compatibility hazards: `get_poltype_desc()` calls `keys.sort()` on a `dict_keys` view. `verify_ports()` accepts port `65536` even though TCP/UDP ports stop at `65535`. `get_all_users()` blindly removes `system_u` and `root`, which can raise if a policy lacks either. `set_use_tmp()` updates default path buckets but never assigns `self.use_tmp`, so tmp rules/types may not be generated consistently. Symbol heuristics have duplicate keys, so earlier mappings are overwritten; for example multiple `openlog` and `pam_` assignments collapse to the last value. `gen_symbols()` uses `os.popen("nm -D %s | grep U" % self.program)` without shell quoting and then `exec()` on hardcoded action strings, making executable paths with shell metacharacters dangerous. Path bucketing in `__find_path()` depends on dictionary iteration order and may match broader prefixes before narrower paths. The DNF/RPM discovery code reads available packages, not necessarily installed packages, and may add paths based on package metadata that do not exist locally. Many file writes use plain `open()` without atomic replacement or error cleanup.

## Test signals
Tests should exercise every policy type's generated `.te/.if/.fc/.spec/.sh` shape with deterministic templates, port parsing including invalid ranges and boundaries, network rule generation for known and unknown port types, default path bucketing, `NEWTYPE` suffix validation, required existing-domain/program errors, RPM/DNF discovery with mocked package APIs, shell-symbol scanning without invoking a real shell, and output file permissions. Regression tests should cover `set_use_tmp()`, `get_poltype_desc()`, and unsafe program paths.
