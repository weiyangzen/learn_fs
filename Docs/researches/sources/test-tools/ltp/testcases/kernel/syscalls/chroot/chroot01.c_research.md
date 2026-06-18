# sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot01.c

Purpose: verifies unprivileged `chroot()` fails with `EPERM`. Setup records the tmpdir path, looks up nobody, and drops effective uid to nobody; run calls `chroot(path)` expecting EPERM. Important APIs are `tst_tmpdir_path`, `SAFE_GETPWNAM`, `SAFE_SETEUID`, and `chroot`. State is process credentials and tmpdir path. Dependencies are root to drop privileges and a nobody account. Risks are capability retention that could allow chroot unexpectedly. Test signal is `EPERM`.
