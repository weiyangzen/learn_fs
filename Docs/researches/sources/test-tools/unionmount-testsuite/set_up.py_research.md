# sources/test-tools/unionmount-testsuite/set_up.py

Purpose: cleans previous suite mounts and creates the reusable lower-layer fixture tree for unionmount tests.

Important APIs/types/functions: `create_file`, `clean_up`, and `set_up`.

Control flow: `clean_up` syncs and repeatedly unmounts old union, lower, upper, per-layer, and base mounts regardless of current config. `set_up` mounts/prepares base and lower roots as needed, creates the lower test directory, records path components in the context tree, sets cwd, and for file numbers 100-129 creates regular files, direct/indirect symlinks, dangling symlinks, populated directories, empty directories, dir symlinks, root-owned files, and missing path records. It optionally converts the lower tree into squashfs or erofs, or remounts lower read-only for overlay tests.

State and persistence: creates/mounts lower/base filesystems and populates the lower fixture tree; updates context shadow dentries and lower device ID.

Dependencies and integration: called before every test script by `run`. Depends on mount helpers from `tool_box`, `os`, `shutil`, and external `mksquashfs`/`mkfs.erofs` when requested.

Risks: aggressive cleanup unmounts broad globbed paths; fixture ownership assumes uid/gid 1 for `bin`; read-only image tooling must exist for squashfs/erofs modes; repeated setup removes existing lower testdir.

Test signals: all test scripts depend on the fixture names and contents created here.
