# sources/sync-backup/borg/scripts/make-testdata/test_transfer_upgrade.sh

Purpose: Generates Borg 1.2 repository test data for `borg transfer --upgrader=From12To20` and stores it as `src/borg/testsuite/archiver/repo12.tar.gz`.

Important APIs/types/functions: Shell variables select `BORG=./borg-1.2.2`, `TAR=gtar`, `SRC=/tmp/borgtest`, `BORG_REPO=/tmp/repo12`, metadata directory, passphrase, and delete confirmation environment. Uses Borg 1.2 commands `init`, `create`, `list --json-lines`, `list --json`, `--version`, and `delete`.

Control flow: Initializes a repokey repository, creates archive1 with regular file, hardlinks, symlink, broken symlink, FIFO, xattrs, and flags; records list JSON. Creates archive2 with root-only block/char devices and unusual UID/GID via sudo; records list JSON. Captures Borg version and repo list, tars the repository, then deletes it.

State and persistence: Writes temporary data under `/tmp/borgtest` and `/tmp/repo12`, metadata under `/tmp/repo12/test_meta`, and final tarball under the source tree. Uses sudo for special files and cleanup.

Dependencies and integration points: Requires Borg 1.2.2 binary, GNU tar as `gtar`, macOS-style `xattr`/`chflags` commands, sudo permissions, and filesystem support for FIFOs/devices/xattrs/flags. The resulting fixture supports transfer/upgrade tests.

Risks: Destructive fixed `/tmp` paths can collide with existing data. No `set -e`, so partial failures can create invalid fixtures. Platform-specific commands make it non-portable.

Test signals: After generation, run Borg transfer upgrade tests using the fixture and compare stored `archive*_list.json` metadata. Manually verify the tarball contains expected repo and `test_meta` files.
