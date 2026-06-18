# sources/storage-engines/badger/Makefile

Purpose: top-level build helper for Badger CLI, tests, jemalloc installation, and system dependencies.

Important flow: `badger` depends on `jemalloc` and delegates to `make -C badger badger`; `test` depends on `jemalloc` and runs `./test.sh`; `jemalloc` downloads, configures, builds, and installs jemalloc 5.3.1 when `/usr/local/lib/libjemalloc.a` is missing; `dependency` installs apt packages needed by CI.

State and persistence: outputs include installed jemalloc in system locations, downloaded temporary sources under `/tmp/jemalloc-temp`, Badger binary artifacts in the `badger` subdir, and test logs. Dependencies are curl, tar, build tools, sudo, apt, and network access. Risks: build targets mutate system state, sudo may block noninteractive environments, network download is not checksum-verified, and test behavior depends on `test.sh`. Test signals are CI dependency install, jemalloc detection, Badger binary build, and full test run.
