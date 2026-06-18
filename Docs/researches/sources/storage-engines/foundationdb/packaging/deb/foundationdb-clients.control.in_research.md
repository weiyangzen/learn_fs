# sources/storage-engines/foundationdb/packaging/deb/foundationdb-clients.control.in

Purpose: This Debian control template defines metadata for the `foundationdb-clients` package. Build tooling substitutes `VERSION-RELEASE` before packaging.

Important fields: It declares package name, version placeholder, database section, optional priority, `amd64` architecture, conflict with old `foundationdb (<< 0.1.4)`, dependency on `libc6` and `adduser`, maintainer, homepage, and description.

Control flow: There is no executable control flow; Debian tooling reads the generated control file during package build/install.

State and persistence behavior: Package metadata affects dependency resolution and installed package identity, not application runtime state.

Dependencies and integration points: It integrates with `builddebs.sh` and Debian packaging conventions. The clients package contains utilities, headers, and libraries used by applications and by the server package dependency.

Risks: Architecture is fixed to `amd64`, which must match artifact builds. Dependency versions may become stale for newer distributions. Tests should render the template and validate it with `dpkg-deb`/`lintian` or package install smoke tests.
