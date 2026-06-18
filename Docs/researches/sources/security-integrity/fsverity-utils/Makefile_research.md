# sources/security-integrity/fsverity-utils/Makefile

Purpose: The Makefile is the main build, install, test, clean, and release orchestration for fsverity-utils. It builds the `fsverity` CLI, `libfsverity`, tests, headers, pkg-config metadata, and optional documentation.

Important APIs and targets: Key targets include default build, `install`, `uninstall`, `check`/tests, `clean`, static/shared library outputs, program objects, and generated `libfsverity.pc`. Variables configure `CC`, `CFLAGS`, `LDFLAGS`, prefix/libdir/include paths, OpenSSL/libcrypto support, and versioning.

Control flow and state: It compiles C sources into object files, links programs and libraries, stages installation paths, and writes generated pkg-config data. Build state is object files, libraries, binaries, and generated metadata.

Dependencies and integration points: Integrates with `common/`, `lib/`, `programs/`, `scripts/run-tests.sh`, pkg-config, Linux headers, and OpenSSL-compatible crypto libraries.

Risks and test signals: Build flags must stay ABI-compatible for `libfsverity`. Risks include platform-specific linker flags, library soname/version errors, and optional crypto backend differences. Signals are clean rebuilds, installed header/library layout, pkg-config correctness, and test target success.
