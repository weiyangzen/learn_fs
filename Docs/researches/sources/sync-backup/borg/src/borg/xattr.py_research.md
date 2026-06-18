# sources/sync-backup/borg/src/borg/xattr.py

## Purpose
Provides Borg's high-level extended attribute operations across Linux, FreeBSD, and macOS, including fakeroot detection and tolerant bulk get/set helpers.

## Important APIs, Types, and Functions
Exports `XATTR_FAKEROOT`, `is_enabled(path=None)`, `get_all(path, follow_symlinks=False)`, and `set_all(path, xattrs, follow_symlinks=False)`. Re-exports/imports platform functions `listxattr`, `getxattr`, `setxattr`, and `ENOATTR`.

## Control Flow
At import time, Linux fakeroot support is detected by scanning `LD_PRELOAD` for `libfakeroot`, running `fakeroot -v`, and requiring version at least 1.20.2. `is_enabled` writes and reads a temporary user xattr. `get_all` lists names, reads values individually, ignores disappearing attrs, and warns on unreadable attrs. `set_all` applies each attr and returns a warning flag.

## State and Persistence Behavior
State is filesystem xattrs on caller paths. Empty values use `None` in the all-xattrs mapping. Import-time `XATTR_FAKEROOT` is process-global and reflects the startup environment.

## Dependencies and Integration Points
Depends on platform xattr bindings, `packaging.version`, subprocess environment preparation, and Borg logging. Used by metadata backup/restore and tests that require xattr round trips.

## Risks and Test Signals
Risks include filesystem/platform unsupported errors, races between list and get, warning-only restoration failures, fakeroot subprocess dependency, and confusing `None` vs empty bytes. Tests should exercise unsupported filesystems, EPERM/EINVAL warning paths, empty values, symlinks, and fakeroot environment combinations.
