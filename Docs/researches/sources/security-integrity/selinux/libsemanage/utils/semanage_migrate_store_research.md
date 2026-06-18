# sources/security-integrity/selinux/libsemanage/utils/semanage_migrate_store

## Purpose
`semanage_migrate_store` is a Python 3 utility for migrating SELinux policy stores from the older `/etc/selinux/<store>/modules/active` module layout to the newer `/var/lib/selinux/<store>/active/modules/<priority>` layout. It can migrate one selected store or every store under the old root, optionally clean old modules, and optionally rebuild policy.

## Important APIs, Types, and Functions
Important functions are `copy_file`, `create_dir`, `create_file`, `copy_module`, `disable_module`, `migrate_store`, `rebuild_policy`, and path helpers such as `oldroot_path`, `oldstore_path`, `oldmodules_path`, `newroot_path`, `newstore_path`, `newmodules_path`, `disabledmodules_path`, and `bottomdir_path`.

The script imports Python `os`, `errno`, `shutil`, `sys`, `optparse.OptionParser`, and the SELinux Python bindings `selinux` and `semanage`. CLI options include `--priority`, `--store`, `--debug`, `--clean`, `--norebuild`, `--path`, and `--root`.

## Control Flow
Startup imports SELinux bindings and exits with a diagnostic if unavailable. Main option parsing initializes global settings: `DEBUG`, `PRIORITY`, `TYPE`, `CLEAN`, `NOREBUILD`, `PATH`, `ROOT`, and `TOPPATHS`. It ensures the new root exists, determines stores either from `--store` or by listing the old root, skips entries without an old modules directory, and skips stores whose new active store already exists.

`migrate_store` creates the new active/module/disabled directories, copies `base.pp` specially from the old active root, then walks old top-level files and module files. Top-level files in `TOPPATHS` are copied to the new active store, with `seusers` renamed to `seusers.local`. Module `.pp` files are copied into priority subdirectories as `hll` with `lang_ext` set to `pp`; `.disabled` markers become files in `active/modules/disabled`; stray non-`.pp` module files produce warnings. After migration, `--clean` removes the old modules directory. Unless `--norebuild` is set, `rebuild_policy` opens a direct semanage handle for the current policy type and commits a rebuild transaction.

## State and Persistence Behavior
The script performs privileged filesystem migration. It creates directories with modes `0755` or `0700`, copies store files, creates module `hll` and `lang_ext` files, creates disabled markers, and may delete the old modules directory with `shutil.rmtree`. Rebuild state is persisted through libsemanage transaction commit.

## Dependencies and Integration Points
It integrates old `/etc/selinux` stores, new `/var/lib/selinux` stores, libselinux policy-type discovery, and libsemanage direct-store rebuild. It is installed by `utils/Makefile` into SELinux libexec.

## Risks and Edge Cases
The script exits on most copy/create failures and does not roll back partially migrated stores. It skips stores if the new active directory already exists, even when the old modules directory remains. It treats `base.pp` name conflicts in the module directory as fatal. `copy_module` opens `lang_ext` with `open(path, "w+", 0o600)`, where the third argument is buffering, not file mode, in Python's built-in `open`; actual file permissions depend on normal creation defaults and umask. Running with `--clean` can remove old modules after partial success.

## Test Signals
Signals include printed migration lines, expected new directory layout under `PATH`, copied top-level local files, module subdirectories under the configured priority containing `hll` and `lang_ext`, disabled marker files, warnings for skipped invalid files, and a successful semanage rebuild unless `--norebuild` is used.
