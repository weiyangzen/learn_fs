# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/configure

## Summary
Generated GNU Autoconf 2.69 `configure` script for `rumpuser-posix 999`, producing `rumpuser_config.h` from `rumpuser_config.h.in`.

## Key Details
- Implements standard Autoconf shell setup: portable shell re-exec, option parsing, cache handling, compiler/preprocessor discovery, canonical build/host/target detection, and `config.status` generation.
- Enables large-file probing through `_FILE_OFFSET_BITS`, `_LARGE_FILES`, and related compiler option checks.
- Checks standard headers plus rumpuser-specific portability headers: `sys/param.h`, `sys/sysctl.h`, `sys/disk.h`, `sys/disklabel.h`, `sys/dkio.h`, `sys/atomic.h`, `paths.h`, and `sys/cdefs.h`.
- Checks types `clockid_t` and `register_t`.
- Checks functions used by the POSIX rumpuser layer, including `kqueue`, `chflags`, `strsuftoll`, `setprogname`, `getprogname`, `getenv_r`, memory-alignment routines, `arc4random_buf`, `getsubopt`, `fsync_range`, `__quotactl`, `utimensat`, `preadv`, and `pwritev`.
- Probes `clock_gettime` and `clock_nanosleep` directly and via `-lrt`, and probes `dlinfo` via `-ldl`.
- Detects `struct sockaddr_in.sin_len`, two-argument and three-argument `pthread_setname_np`, and whether `ioctl` takes an `int` command argument.

## Notes
This is a generated artifact; `configure.ac` is the compact authoritative source for the project-specific checks. The generated script still matters for bootstrap behavior on systems without Autoconf.
