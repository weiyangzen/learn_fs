# sources/test-tools/ltp/testcases/kernel/syscalls/chroot/chroot04.c

Purpose: verifies unprivileged `chroot()` to a directory without search permission fails with `EACCES`. Setup creates `chroot04_tmpdir` with mode 0222, looks up nobody, and drops euid. Run calls `chroot` on that directory expecting EACCES. Important APIs are `SAFE_MKDIR`, `SAFE_GETPWNAM`, `SAFE_SETEUID`, and `chroot`. State is a tmpdir directory with no execute/search bit and process credentials. Dependencies are root and permission semantics. Risks include filesystems ignoring directory mode. Test signal is `EACCES`.
