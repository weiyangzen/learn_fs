# sources/sync-backup/borg/src/borg/testsuite/archiver/__init__.py

Purpose: central test harness for Borg archiver command tests. It abstracts invoking Borg in-process or through a forked/binary executable, creates common repository/source fixtures, and supplies filesystem assertion helpers.

Important APIs/types/functions: `exec_cmd` runs Borg either by `subprocess.check_output` or by constructing an `Archiver`, parsing args, redirecting stdio to buffers, running `archiver.run`, and flushing logging. `cmd_fixture`, `generate_archiver_tests`, `checkts`, and `cmd` provide parametrized command execution with repository injection and exit-code assertions. Setup helpers include `create_src_archive`, `open_archive`, `open_repository`, `create_regular_file`, `create_test_files`, `_extract_repository_id`, `_set_repository_id`, cache/tagged fixture builders, and hardlink setup. Assertion/context helpers include `assert_creates_file`, `assert_dirs_equal`, `assert_line_exists`, `assert_line_not_exists`, `read_only`, `wait_for_mountstate`, and `fuse_mount`.

Control flow: tests call `cmd(archiver, ...)`, which prepends `--repo`, selects fork behavior from the fixture, asserts expected return code, and filters pure-Python msgpack warnings. `create_test_files` builds a representative tree with regular files, directories, permissions, hardlinks, symlinks, xattrs, FIFO, flags, devices, ownership, and a newer empty file, skipping unsupported operations. `assert_dirs_equal` recursively compares file type, mode, uid/gid/rdev, nlink, flags, mtime, and xattrs with FUSE/timestamp adjustments. `fuse_mount` handles forked Borg mount, OS double-fork mode, wait/umount cleanup, and expected mount failure cases.

State and persistence behavior: creates and mutates temporary input/output/repository/cache trees owned by test fixtures. It may alter file flags, permissions, xattrs, hardlinks, and mountpoints. In-process command execution temporarily replaces `sys.stdin`, `sys.stdout`, and `sys.stderr` and restores them in `finally`.

Dependencies and integration points: depends on `Archiver`, repository/manifest/archive classes, Borg constants, platform feature probes from `borg.testsuite`, xattr/platform modules, and OS utilities such as chmod/chattr/chflags/umount. Nearly every command test imports this module.

Risks: global stdio replacement in `exec_cmd` is fragile under concurrency. Device, flag, xattr, fakeroot, FUSE, and binary/fork behavior varies by platform. `read_only` shells out and skips when immutable flags cannot be set. `assert_dirs_equal` encodes many platform-specific comparison relaxations and can fail when host metadata is injected.

Test signals: this harness is itself validated indirectly by broad command suites across local, remote, and binary modes. Failures here usually cascade widely, making it a high-impact integration point.
