# sources/user-network-fs/sshfs/test/test_sshfs.py

## Purpose

`test_sshfs.py` is the main integration and regression test suite for the SSHFS userspace filesystem. It mounts the locally built `sshfs` binary against a passwordless `localhost` SSH/SFTP server, then verifies that ordinary POSIX filesystem operations through the FUSE mount behave like operations on the backing source directory. The file also contains targeted option tests for hardlink disabling, symlink following and containment, direct I/O, and malformed SFTP reply handling.

The suite is intended to run under pytest and can be invoked directly because the `__main__` block calls `pytest.main([__file__] + sys.argv[1:])`. It is not a unit-test-only file: most tests require FUSE support, a working `fusermount`/`fusermount3`, the built `sshfs` executable, and passwordless SSH to `localhost`.

## Important APIs, Types, And Functions

- `pytestmark = fuse_test_marker()` applies an environment-sensitive pytest marker from `util.py`, skipping the module when FUSE prerequisites are unavailable.
- `TEST_DATA` reads the current test file as binary data and is reused by read/write/truncate tests as stable nontrivial file content.
- `name_generator()` uses a mutable default counter to generate process-local unique names such as `testfile_1`; this keeps operations from colliding inside a shared temporary mount.
- `test_sshfs(tmpdir, debug, cache_timeout, sync_rd, multiconn, capfd)` is the broad matrix test. It runs across `debug`, directory cache timeout, `sync_readdir`, and `max_conns=3` permutations, mounts SSHFS in foreground mode, then calls the `tst_*` operation helpers.
- `_check_ssh_localhost()` duplicates the passwordless localhost SSH probe used by the main matrix and fails the test on timeout or nonzero exit.
- `_mount_sshfs(tmpdir, extra_opts=None)` and `_sshfs_mount(src_dir, mnt_dir, extra_opts=None)` are reusable mount helpers for option-specific tests; the latter is a context manager.
- `tst_*` helpers exercise individual filesystem semantics: unlink, mkdir/rmdir, rename/rename-over/rename-sibling/rename-open-release, chmod/chown, fsync, symlink, create, open/read/write/append/seek, statvfs, access, hardlink, readdir, path/fd truncate, utimens, passthrough visibility, open-unlink, write-only reads, and repeated readdir consistency.
- Option regression tests include `test_disable_hardlink`, `test_follow_symlinks`, `test_direct_io`, `test_bad_sftp_reply_len`, `test_contain_symlinks`, `test_no_contain_symlinks`, `test_transform_with_contain`, and `test_contain_symlinks_option_precedence`.

## Control Flow

The module first ensures it can SSH into `localhost` without prompting by running `ssh -o StrictHostKeyChecking=no -o KbdInteractiveAuthentication=no -o ChallengeResponseAuthentication=no -o PasswordAuthentication=no localhost -- true` with a 10 second timeout. The main matrix then creates isolated `mnt` and `src` directories under pytest's `tmpdir`, builds a command beginning with `base_cmdline`, the built `sshfs` path, `-f`, `localhost:<src_dir>`, and the mountpoint, and appends options according to the parameter set.

The main command always disables FUSE entry and attribute caching with `entry_timeout=0` and `attr_timeout=0`, disables symlink containment with `no_contain_symlinks` for the legacy symlink helper, and sets `G_DEBUG=fatal-warnings` so GLib warnings abort the mounted process. After `subprocess.Popen`, `wait_for_mount()` polls until the mount appears or the process dies. The test then executes the operation helpers in a fixed sequence and unmounts with `umount()` on success. On any exception, `cleanup()` attempts lazy unmount and terminates or kills the mount process before reraising.

The helper tests follow the same lifecycle in smaller scopes. `_mount_sshfs()` creates a fresh source and mount directory, appends arbitrary `-o` options, waits for the mount, and returns process plus paths. `_sshfs_mount()` wraps that pattern as a context manager for symlink containment scenarios. `test_bad_sftp_reply_len` is different: it generates an executable Python SFTP stub that emits a normal version packet followed by a zero-length reply, starts `sshfs` with `ssh_command=<helper>`, and asserts that SSHFS fails with `bad reply len: 0`.

## State And Persistence Behavior

All filesystem state is intentionally temporary. Pytest's `tmpdir` owns the source and mount directories, and `name_generator()` provides per-process unique leaf names. The tests create files, directories, hardlinks, symlinks, open file descriptors, metadata changes, and timestamps both through the mounted view and directly in the backing source directory. Cache-sensitive tests call `safe_sleep(cache_timeout + 1)` when directory-cache visibility can lag.

The only persistent host-side state risk is SSH known-host and key setup: `StrictHostKeyChecking=no` can add a localhost key warning, which the custom `capfd.register_output()` filter treats as expected output. Mount processes are external stateful processes; the suite relies on `umount()`/`cleanup()` to avoid leaving mounted tmpdirs behind. No durable repository files are written by this test, except the generated helper inside `tmpdir` for `test_bad_sftp_reply_len`.

## Dependencies And Integration Points

- Imports from `util.py`: `wait_for_mount`, `umount`, `cleanup`, `base_cmdline`, `basename`, `fuse_test_marker`, `safe_sleep`, `os_create`, and `os_open`.
- Pytest supplies `tmpdir`, `capfd`, parametrization, skip/fail helpers, and exception assertions. `capfd.register_output()` is a project-specific extension installed by `test/conftest.py`.
- The built SSHFS executable is addressed as `pjoin(basename, "sshfs")`, where `basename` points one directory above `test/`.
- System integration requires OpenSSH client/server, passwordless localhost authentication, FUSE kernel support, `fusermount` for capability detection/cleanup, and `fusermount3` for normal unmounts.
- Standard library dependencies include `subprocess`, `os`, `sys`, `stat`, `shutil`, `filecmp`, `errno`, `NamedTemporaryFile`, and `contextmanager`.
- Meson includes this file through `test/meson.build`, and the CI scripts run it via `python3 -m pytest --maxfail=99 test/`.

## Risks And Edge Cases

- The test suite is highly environment-sensitive. Missing `/dev/fuse`, missing setuid `fusermount` for non-root users, absent `fusermount3`, or no passwordless localhost SSH causes skips or failures unrelated to SSHFS logic.
- `_check_ssh_localhost()` is duplicated instead of reused from the main test body, which can drift if SSH options need updating.
- `name_generator()` uses a mutable default counter, which is acceptable for one process but is not designed for cross-process coordination if tests are parallelized in the same mount directory.
- Cache-sensitive assertions depend on sleep-based expiry; slow filesystems or changed cache semantics can introduce flakiness.
- The main matrix can be expensive: it runs a large operation sequence across 16 combinations and, with `TEST_WITH_VALGRIND=true`, every SSHFS mount runs under Valgrind through `base_cmdline`.
- Some assertions are platform-specific. `tst_chown` only runs as root; symlink opt-out reads `/etc/passwd`; hardlink behavior depends on server extension support; timestamp tolerance is one second for SSHFS set-time semantics.
- `test_bad_sftp_reply_len` assumes the expected diagnostic string is stable, so error-message wording changes can break it even if the behavior remains safe.

## Test Signals

- Passing `test_sshfs` across all parameter combinations signals that core create/read/write/metadata/directory operations work with and without SSHFS directory caching, sync readdir, debug logging, and multiconnection mode.
- `test_disable_hardlink` verifies both the control path where hardlinks work and the `disable_hardlink` option path where `os.link` fails with `ENOSYS` or `EPERM`.
- `test_follow_symlinks`, `test_contain_symlinks`, `test_no_contain_symlinks`, `test_transform_with_contain`, and `test_contain_symlinks_option_precedence` collectively cover symlink resolution policy, escape blocking, transform interactions, and last-option-wins parsing.
- `test_direct_io` covers the `direct_io` option by writing through the mount and verifying both mounted and backing-store reads.
- `test_bad_sftp_reply_len` is a negative protocol test that protects against zero-length SFTP reply underflow.
- Expected-output filters for SSH known-host warnings and transform warnings make unexpected stdout/stderr noise a useful failure signal through the project's pytest capture extension.
