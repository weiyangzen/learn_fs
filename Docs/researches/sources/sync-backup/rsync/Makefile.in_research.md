# sources/sync-backup/rsync/Makefile.in

Purpose: autoconf template for building, installing, testing, generating, and cleaning rsync.

Important APIs/types/functions: defines configured variables, object groups, generated headers/docs, install/uninstall targets, build targets for `rsync`, `tls`, test helpers, `rrsync`, generated manpages, `proto.h`, coverage targets, protocol check targets, and maintenance targets.

Control flow: `configure` substitutes placeholders into `Makefile`. Normal `all` builds rsync, stunnel config, optional rrsync, and manpages. `check` depends on helper programs and symlinked fake tests, then runs `runtests.py`. Coverage targets guard for coverage flags, run tests, and invoke gcovr.

State and persistence: creates object files, generated headers, manpages, coverage directories, testtmp dirs, installed files under DESTDIR/prefix, and artifacts consumed by CI.

Dependencies/integration: coordinates C compiler, AWK generators, autoconf, bundled zlib/popt, optional SIMD/asm, test suite, and docs conversion.

Risks: generated-file dependency ordering matters under parallel make; Android workflow explicitly prebuilds `proto.h`. Install/uninstall target drift is caught by Ubuntu CI.

Test signals: `make check`, `check29`, `check30`, `coverage`, `coverage-tcp`, and CI install smoke.
