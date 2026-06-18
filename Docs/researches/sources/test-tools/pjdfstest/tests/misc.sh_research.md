<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pjdfstest/tests/misc.sh -->
# sources/test-tools/pjdfstest/tests/misc.sh

Purpose: shared shell library for pjdfstest TAP-style filesystem tests. It locates the project configuration and `pjdfstest` binary, provides expectation helpers, random name/path generators, feature gating, mount-option probes, and fixture creation helpers.

Important APIs/types/functions: `expect()` and `jexpect()` run pjdfstest commands locally or inside a FreeBSD jail and emit `ok/not ok` with incrementing `ntest`. `test_check()` wraps shell predicates. `todo()` marks OS/filesystem-specific expected failures. `namegen*()` and `dirgen_max()` produce random names at requested or filesystem maximum lengths. `supported()` and `require()` gate features such as `lchmod`, `chflags`, `link`, `posix_fallocate`, `rename_ctime`, `stat_st_birthtime`, `utimensat`, and `UTIME_NOW`. FreeBSD-only helpers report mount options, NFSv4 ACL support, `noexec`, and `nosuid`. `create_file()` creates typed filesystem objects and applies optional mode/ownership.

Control flow/state: sourcing the file initializes `ntest`, `confdir`, `maindir`, `fstest`, imports `conf`, and exits early on missing configuration/binary. Runtime state is shell globals such as `todomsg`, `os`, `fs`, and TAP counter.

Dependencies/integration: depends on `/bin/sh`, `dd`, `openssl md5`, `awk`, `grep`, `jail` for jail paths, and pjdfstest command semantics. It is included by many pjdfstest test scripts.

Risks/test signals: unquoted variables can mis-handle spaces in paths; random generators depend on OpenSSL output format. The TAP output itself is the test signal, and `quick_exit()` is used to count unsupported feature tests as skipped/successful according to suite convention.
<!-- END_FILE_RESEARCH: sources/test-tools/pjdfstest/tests/misc.sh -->
