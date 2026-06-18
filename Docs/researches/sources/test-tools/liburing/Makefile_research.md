# sources/test-tools/liburing/Makefile

## sources/test-tools/liburing/Makefile

Purpose: Top-level build orchestration for liburing. It delegates library, test, and example builds, generates pkg-config files, installs/uninstalls library/manpage/test artifacts, and supports source archives and SRPMs.

Important targets/APIs: `all`, `library`, `runtests`, `runtests-loop`, `runtests-parallel`, `config-host.mak`, `%.pc`, `install`, `uninstall`, `install-tests`, `clean`, `archive`, and `srpm`. It includes `Makefile.common`, `Makefile.quiet` indirectly through subdirs, and `config-host.mak` after auto-running `configure`.

Control flow: `all` recursively builds `src`, `test`, and `examples`. If not cleaning, `config-host.mak` is included and regenerated via `configure` when absent/out-of-date. Pkg-config files are generated from `.pc.in` templates using `sed`. Install recurses into `src`, writes pkg-config files, and installs manpages.

State and persistence: writes `config-host.mak`, `config-host.h`, `liburing.pc`, `liburing-ffi.pc`, build outputs, installed headers/libs, manpages, and archive/SRPM files. Clean removes local generated config and artifacts plus delegated subdir outputs.

Dependencies/integration: relies on `configure` for feature detection, recursive `make` in `src`, `test`, and `examples`, RPM tooling for `srpm`, git for archives/tags, and install paths from config.

Risks: recursive make hides some dependency edges. `config-host.mak` replays the old configure command by parsing a comment, which can break if quoting is complex. Install directly writes into configured paths and must be combined carefully with `DESTDIR`.

Test signals: `make all`, `make runtests*`, `make install`, CI out-of-source and install smoke tests.
