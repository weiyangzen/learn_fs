# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/defaults.py

## Purpose
This module centralizes default filesystem paths for sepolgen data, generated interface metadata, permission maps, attributes, reference-policy makefiles, and include headers. It also provides a configurable search-path helper.

## Important APIs, types, and functions
- `PathChooser(pathname)` reads a simple `key = value` configuration file or installs default `SELINUX_DEVEL_PATH` values when the config file is absent.
- `PathChooser.__call__(testfilename, pathset="SELINUX_DEVEL_PATH")` searches the configured colon-separated path list for `testfilename`, returning the first existing path or a fallback under the first configured directory.
- `data_dir()`, `perm_map()`, `interface_info()`, and `attribute_info()` return `/var/lib/sepolgen` paths.
- `refpolicy_makefile()` uses `PathChooser("/etc/selinux/sepolgen.conf")` to locate `Makefile`, falling back to `include/Makefile`.
- `headers()` locates the reference-policy `include` directory.

## Control flow
Constructing `PathChooser` either sets default search paths or parses each nonblank, noncomment config line with a `key = value` regex. Calling the object splits the selected pathset on `:`, tests each candidate path with `os.path.exists()`, and returns the first hit.

## State and persistence behavior
The object stores parsed configuration in memory and performs no writes. The module reads `/etc/selinux/sepolgen.conf` when helper functions construct a chooser.

## Dependencies and integration points
It imports `os` and `re`. Other sepolgen modules can call these helpers to find installed data under `/var/lib/sepolgen` and reference-policy development files under `/usr/share/selinux/default`, `/usr/share/selinux/mls`, or `/usr/share/selinux/devel` unless overridden by config.

## Risks and edge cases
- Config parsing rejects any nonblank/noncomment line that is not exactly `word = value` shaped.
- Missing pathsets raise `ValueError`; missing files return a best-effort path under the first configured directory, so callers must check existence if required.
- A new `PathChooser` is constructed on every `refpolicy_makefile()` or `headers()` call; there is no cache.
- Defaults are hard-coded Linux distribution paths.

## Test signals
Unit tests can create temporary config files, verify default behavior when absent, check invalid-line errors, and test search precedence. Filesystem integration tests can verify `refpolicy_makefile()` fallback from `Makefile` to `include/Makefile`.
