<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/python/ecryptfsapi.py -->
# sources/security-integrity/ecryptfs-utils/src/python/ecryptfsapi.py

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/python/ecryptfsapi.py_research.md`. Source lines read for this pass: 82.

## Purpose
Legacy Python 2 convenience API for toggling eCryptfs private-directory automount/autounmount, invoking mount and unmount helpers, and checking whether setup is needed.

## Important APIs, Types, And Functions
Module constants name `~/.ecryptfs/auto-mount`, `auto-umount`, `Private.mnt`, and derived `PRIVATE_LOCATION`. Functions include `set_automount`, `get_automount`, `set_autounmount`, `get_autounmount`, `set_mounted`, `get_mounted`, and `needs_setup`.

## Control Flow
Setter functions build shell commands (`touch`, `rm`, `/sbin/mount.ecryptfs_private`, `/sbin/umount.ecryptfs_private`) and run them with `commands.getstatusoutput`. Getter functions use `os.path.exists` or scan `/proc/mounts` for `Private.mnt`.

## State And Persistence Behavior
Persists user preferences by creating or removing files in `~/.ecryptfs`; mount state is external in `/proc/mounts` and the eCryptfs helper.

## Dependencies And Integration Points
Depends on Python 2 `commands`, `os`, user home expansion, `/proc/mounts`, and setuid private mount helpers.

## Risks And Edge Cases
Shell command construction is unquoted, Python 2-only, and uses import-time `PRIVATE_LOCATION`, so changes after import are not seen. `needs_setup` has an unimplemented encrypted-home check.

## Test Signals
Test signals are simple file toggle checks plus helper invocation smoke tests under a configured eCryptfs user.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/python/ecryptfsapi.py -->
