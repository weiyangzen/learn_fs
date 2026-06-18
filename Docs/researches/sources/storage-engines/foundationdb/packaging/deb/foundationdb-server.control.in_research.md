# sources/storage-engines/foundationdb/packaging/deb/foundationdb-server.control.in

Purpose: This Debian control template defines metadata for the `foundationdb-server` package. Build tooling substitutes the `VERSION-RELEASE` placeholder.

Important fields: It declares package name, version, database section, optional priority, `amd64` architecture, conflict with old monolithic FoundationDB packages, exact dependency on matching `foundationdb-clients`, `adduser`, `libc6`, recommendation for Python, maintainer, homepage, and description.

Control flow: There is no executable flow; Debian package tools consume this metadata.

State and persistence behavior: The metadata controls installation dependencies and package identity. Runtime state is managed by maintainer scripts and installed binaries, not this template.

Dependencies and integration points: It ties server package installation to the same-version clients package, ensuring `fdbcli` and client libraries are available for post-install configuration and operation.

Risks: Fixed `amd64` architecture and Python recommendation may age poorly. Tests should validate rendered control syntax, dependency resolution, and install/upgrade behavior with the paired clients package.
