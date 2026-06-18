# sources/test-tools/xfstests-bld/fstests-bld/misc/post-reorg-cleanup

Purpose: `post-reorg-cleanup` is a one-time migration helper for cleaning and moving directories after a repository reorganization that introduced/moved `fstests-bld`.

Important APIs, types, and functions: shell variables `CLEAN_DIRS`, `TO_MOVE`, and `NO_ACTION`; CLI supports `--no-action`. It uses `cp`, `mv`, `git clean`, `rm`, and directory checks.

Control flow: validates that `fstests-bld` exists. If `config.custom` exists at top level and not under `fstests-bld`, it explains the split and copies it. It moves configured source directories into `fstests-bld`, moves appliance cache/deb/config directories to `test-appliance`, moves logs/disks to `run-fstests`, renames `kvm-xfstests`, and then either previews or performs `git clean` on old directories and selected nested repos. Finally it removes old version/tarball/script/build outputs.

State and persistence: performs broad filesystem mutation: moves directories, copies config, runs destructive `git clean -fdx`, removes generated files, and deletes build/runtime directories. In `--no-action`, most operations are echoed and `git clean -n` is used.

Dependencies and integration points: intended for a specific repository state immediately after a reorganization commit. It assumes top-level `fstests-bld`, `kvm-xfstests`, `test-appliance`, and `run-fstests` naming.

Risks: destructive and context-sensitive. There is a typo in no-action output using `$CLEAR_DIRS` instead of `$CLEAN_DIRS`, which can make preview misleading. The message says `fststs-bld/` once. It uses many unquoted paths but names are controlled. Running in the wrong repository can remove valuable files after only a simple directory check.

Test signals: use `--no-action` in a fixture repo matching pre/post reorg layouts; inspect printed moves and clean previews. Full execution should only be tested on disposable clones with known expected file moves.
