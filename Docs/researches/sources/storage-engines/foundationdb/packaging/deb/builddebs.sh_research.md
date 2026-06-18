# sources/storage-engines/foundationdb/packaging/deb/builddebs.sh

Purpose: This build script assembles FoundationDB server and client Debian packages from an existing build output tree. It creates temporary package roots, installs files with correct modes, computes installed sizes, and invokes `dpkg-deb`.

Important operations: The server package copies maintainer scripts, config, init script, `fdbserver`, `fdbmonitor`, `make_public.py`, README, and creates data/log/config directories. The client package installs `fdbcli`, `libfdb_c.so`, `libfdb_c_shim.so`, C headers/options, README, `fdbbackup`, and symlinks for backup/restore/DR commands.

Control flow: The script builds server first and client second, accumulating failure count in `status`. Each package uses `mktemp -d`, `fakeroot dpkg-deb --build`, and cleanup with `rm -r`.

State and persistence behavior: It writes package artifacts under `packages` and temporary staging directories. It does not modify system package state.

Dependencies and integration points: It expects to run from a FoundationDB build tree with `bin`, `lib`, `bindings`, `fdbclient`, and `packaging` paths available. It depends on `fakeroot`, `dpkg-deb`, `dos2unix`, and standard Unix install tools.

Risks: Missing build artifacts produce package failures, but cleanup still removes staging directories. The script suppresses `dpkg-deb` stderr, which can hide diagnostics. Tests should verify package contents, modes, symlinks, installed-size fields, maintainer script permissions, and failure reporting for missing inputs.
