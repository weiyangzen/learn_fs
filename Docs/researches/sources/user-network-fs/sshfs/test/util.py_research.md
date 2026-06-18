# sources/user-network-fs/sshfs/test/util.py

## Purpose

`util.py` contains shared pytest helpers for the SSHFS integration tests. It centralizes path discovery for the built `sshfs` binary, small file-descriptor helpers, mount readiness polling, cleanup and unmount behavior, FUSE availability marking, safe sleep across signals, and optional Valgrind command-line prefixing.

## Important APIs, Types, And Functions

- `basename = pjoin(os.path.dirname(__file__), "..")` points from `test/` to the SSHFS build/source root used to locate the `sshfs` executable.
- `os_create(name)` creates an empty read/write file with `os.open(..., O_CREAT | O_RDWR)` and immediately closes it.
- `os_open(name, flags)` is a context manager that yields a raw file descriptor and guarantees `os.close(fd)` in `finally`.
- `wait_for_mount(mount_process, mnt_dir, test_fn=os.path.ismount)` polls for up to 30 seconds until the mountpoint is recognized, failing if the process exits early or the mount never appears.
- `cleanup(mount_process, mnt_dir)` attempts lazy unmount with `fusermount -z -u`, suppresses output, terminates the process, waits one second, and kills it if needed.
- `umount(mount_process, mnt_dir)` performs the normal unmount path with `fusermount3 -z -u`, asserts the path is no longer a mount, and waits up to 30 seconds for a zero process exit code.
- `safe_sleep(secs)` loops around `time.sleep()` until wall-clock time reaches the requested end time, preventing signal-shortened sleeps.
- `fuse_test_marker()` returns either `pytest.mark.uses_fuse()` or a pytest skip marker with a concrete reason after checking `fusermount`, `/dev/fuse`, setuid/root status, and `/dev/fuse` openability.
- `base_cmdline` is `["valgrind", "-q", "--"]` when `TEST_WITH_VALGRIND` is truthy, otherwise an empty list.

## Control Flow

Test modules import these helpers during collection. `fuse_test_marker()` executes at import time in `test_sshfs.py`: it runs `which fusermount`, verifies `/dev/fuse`, allows root directly, checks the setuid bit on `fusermount` for non-root users, and tries to open `/dev/fuse` read/write. The first failed prerequisite becomes a skip reason; otherwise the module receives the `uses_fuse` marker.

At runtime, tests launch SSHFS with `subprocess.Popen`, then call `wait_for_mount()`. That function polls every 0.1 seconds and also checks `mount_process.poll()` to fail early if SSHFS exits before mounting. Successful tests call `umount()`, which uses `fusermount3`, checks the mount disappeared, and polls for process termination. Failing tests call `cleanup()`, which uses the older `fusermount` command for a best-effort lazy unmount and forcefully ends the process if graceful termination fails.

The `base_cmdline` computation is a module-level environment hook. CI can set `TEST_WITH_VALGRIND=true`, causing all test commands that prepend `base_cmdline` to execute SSHFS under Valgrind without changing each test.

## State And Persistence Behavior

This module does not keep durable state. It interacts with system state by probing executables, `/dev/fuse`, file permissions, mount state, and child process status. `cleanup()` and `umount()` mutate mount state by unmounting the FUSE mountpoint and terminating the SSHFS child process. `os_create()` and `os_open()` mutate files only at paths supplied by tests.

The only module-level mutable behavior is `base_cmdline`, derived once from `TEST_WITH_VALGRIND` at import time. Changing that environment variable after import will not affect already imported helpers.

## Dependencies And Integration Points

- Depends on Python standard modules `subprocess`, `os`, `stat`, `time`, `contextmanager`, and `os.path.join`.
- Depends on pytest for `pytest.fail`, skip markers, and `uses_fuse` markers.
- Depends on system `which`, `fusermount`, `fusermount3`, `/dev/fuse`, and optionally `valgrind`.
- Used directly by `test_sshfs.py`; Meson includes `util.py` in the installed/copied test script list via `test/meson.build`.
- `travis-build.sh` controls the Valgrind path through `TEST_WITH_VALGRIND=true`.

## Risks And Edge Cases

- `fuse_test_marker()` checks for `fusermount`, but `umount()` later requires `fusermount3`; an environment with only `fusermount` can collect tests but fail during teardown.
- `cleanup()` and `umount()` use different unmount binaries, which may reflect compatibility needs but can produce inconsistent behavior on systems where only one is installed.
- The mount wait and unmount wait are fixed 30 second loops with 0.1 second sleeps; very slow CI can fail even if the operation would eventually complete.
- `cleanup()` suppresses unmount output, which keeps logs quiet but can hide useful diagnostics.
- `wait_for_mount()` only reports premature termination, not stderr; diagnosing mount failures depends on surrounding pytest capture.
- Valgrind presence is not validated when `TEST_WITH_VALGRIND` is set; missing Valgrind will fail later at process launch.

## Test Signals

- Environment skip reasons from `fuse_test_marker()` distinguish missing `fusermount`, unloaded FUSE kernel support, missing setuid permission, and inability to open `/dev/fuse`.
- `wait_for_mount()` failing with "file system process terminated prematurely" signals SSHFS crashed or exited before mounting.
- `umount()` failing with a nonzero mount process code signals runtime errors detected after unmount.
- Valgrind mode uses the same functional tests while adding memory-error detection around the SSHFS process.
