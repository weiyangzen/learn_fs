# sources/security-integrity/audit-userspace/configure.ac

Purpose: Autoconf entry point for audit-userspace 4.1.5. It configures compiler, libtool, generated headers, run-state paths, optional language bindings, optional daemon/plugin features, architecture syscall table support, sanitizer support, and generated Makefiles.

Important APIs and build outputs: Defines `AUDIT_RUN_DIR`, feature-detection macros for kernel audit headers (`AUDIT_FEATURE_VERSION`, `AUDIT_STATUS_BACKLOG_WAIT_TIME`, `AUDIT_STATUS_BACKLOG_WAIT_TIME_ACTUAL`), libc functions (`posix_fallocate`, `signalfd`, `rawmemchr`, `faccessat`, `mallinfo2`, `close_range`), atomic fallback typedef macros, GCC attribute support probes, and automake conditionals such as `USE_PYTHON3`, `HAVE_GOLANG`, `ENABLE_LISTENER`, `ENABLE_ZOS_REMOTE`, `ENABLE_GSSAPI`, `ENABLE_EXPERIMENTAL`, `USE_ARM`, `USE_AARCH64`, `USE_RISCV`, `HAVE_ASAN`, `BUILD_STATIC`, and `ENABLE_LISTENER`.

Control flow: Initializes package metadata, compiler tools, libev macro state, and runstatedir defaults. It then probes headers/functions, chooses optional Python3 and Go bindings, validates SWIG when Python bindings are enabled, configures network listener and plugin families, checks LDAP for `zos-remote`, conditionally enables GSSAPI, warning flags, ASAN, processor table support, AppArmor, tcp_wrappers, io_uring, nftables/iptables selection, and libcap-ng. It ends by generating Makefiles and systemd/init templates including `init.d/augenrules`.

State and persistence: Configuration decisions persist into `config.h`, substituted Makefiles, `audit.pc`, and generated service/script files. The default runtime directory is forced to `/run/audit` when the user has not overridden `runstatedir`.

Dependencies and integration: Integrates with Autoconf, Automake, Libtool, kernel audit headers, libev, Python `python3-config`, SWIG, Go, OpenLDAP, GSSAPI/Kerberos, tcp_wrappers, libcap-ng, and many subdirectories. Architecture options directly control generated syscall lookup tables in `lib/Makefile.am`.

Risks: Build behavior depends heavily on host headers and optional libraries, so missing kernel definitions or stale headers can silently disable newer audit features. `--with-*` options differ between hard failure and warning paths. The `__attr_access` and `__attr_dealloc_free` probes compile snippets that rely on libc/compiler attribute support. Optional `tcp_wrappers` path handling accepts custom library flags, which needs careful quoting in packaging.

Test signals: Run `autoreconf -fi`, `./configure --help`, and configure matrices with/without Python, Go, LDAP, GSSAPI, libwrap, io_uring, and architecture options. Confirm generated `config.h`, `init.d/auditd.service`, `init.d/audit-rules.service`, `init.d/augenrules`, and `lib/audit.pc` contain expected substitutions.
