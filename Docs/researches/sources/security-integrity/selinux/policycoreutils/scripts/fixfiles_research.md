<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/scripts/fixfiles -->
# sources/security-integrity/selinux/policycoreutils/scripts/fixfiles

## Purpose
Provides high-level SELinux filesystem relabel workflows: check, verify, restore, relabel now, or request relabel on next boot.

## Important APIs, Types, And Functions
Major shell functions are `useseclabel`, `get_all_labeled_mounts`, `get_rw_labeled_mounts`, `get_ro_labeled_mounts`, `get_undefined_type`, `get_unlabeled_type`, `exclude_dirs_from_relabelling`, `LogReadOnly`, `LogExcluded`, `newer`, `diff_filecontext`, `rpmlist`, `fix_labels_on_mountpoint`, `restore`, `fullrelabel`, `relabel`, `process`, `usage`, and `set_restore_mode`. It drives `/sbin/setfiles`, `/sbin/restorecon`, `secon`, `find`, `rpm`, `genhomedircon`, `mount --bind`, `unshare -m`, `chcon`, and `selinuxenabled`.

## Control Flow
Startup computes labeled rw/ro mounts and the active `file_contexts` path from `/etc/selinux/config`. Options select force, verbose/progress, boot-time cutoff, previous file-context diff mode, RPM file list mode, bind-mount mode, full `/tmp` cleanup, and thread count. `process()` dispatches commands. `restore()` handles boot-time incremental relabel, file-context diff relabel, RPM-owned paths, explicit paths, or all writable labeled mounts. `relabel()` optionally asks about `/tmp` cleanup; `onboot` writes `/.autorelabel`.

## State And Persistence
The script can relabel large filesystem trees, delete `/tmp` contents, delete selected unlabeled temporary sockets/FIFOs, create temporary bind mount trees under `/run`, write `/.autorelabel`, and redirect logs with the obsolete `-l` option.

## Dependencies And Integration Points
It is the operational front end for `setfiles`/`restorecon`, RPM databases, SELinuxfs initial contexts, `/proc/self/mounts`, `/proc/self/mountinfo`, `/etc/selinux/fixfiles_exclude_dirs`, and boot relabel handling.

## Risks And Edge Cases
The blast radius is high: wrong mount detection, broken excludes, regex simplification in `diff_filecontext`, or `-F` can relabel many files. Bind-mount cleanup must not leave mounts behind. `set -o nounset` makes unset-variable paths fail fast.

## Test Signals
Run shell syntax checks, staged `DESTDIR`/container relabel dry runs, exclude-file parsing tests, RPM mode with missing packages, bind-mount cleanup on failure, `-N`/`-B` incremental modes, and `onboot` content validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/scripts/fixfiles -->
