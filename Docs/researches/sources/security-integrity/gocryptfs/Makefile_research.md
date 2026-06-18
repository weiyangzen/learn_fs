# sources/security-integrity/gocryptfs/Makefile

Purpose: This Makefile wraps common gocryptfs build, install, uninstall, test, clean, and manpage operations.

Important APIs and targets: It delegates to Go build scripts, installs `gocryptfs`, `gocryptfs-xray`, documentation, and auxiliary files under configurable prefix paths, and exposes test/clean targets.

Control flow and state: Targets create binaries, install files, and remove build artifacts. Persistent state is generated binaries and installed filesystem paths.

Dependencies and integration points: Integrates shell build scripts, Go modules, documentation rendering, and packaging conventions.

Risks and test signals: Risks include install path mistakes, missing xray binary, stale manpages, and mismatch with shell scripts. Signals include `make`, `make test`, and staged install checks.
