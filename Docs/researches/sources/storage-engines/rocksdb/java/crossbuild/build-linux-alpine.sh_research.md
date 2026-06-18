<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux-alpine.sh -->
# Research: sources/storage-engines/rocksdb/java/crossbuild/build-linux-alpine.sh

Purpose: Builds portable RocksDB Java artifacts inside an Alpine Linux environment and copies JNI native libraries/JARs to `/rocksdb-build`.

Important APIs/types/functions: The script uses `apk`, repository edits for edge/community, OpenJDK 7 setup, source build of gflags v2.0, `make jclean clean`, `PORTABLE=1 make -j8 rocksdbjavastatic`, and `cp` commands for target artifacts.

Control flow: With `set -e`, it upgrades the Alpine system, installs certificates, build tools, RocksDB compression/dependency packages, Java 7 with certificate symlink repair, removes apk cache, builds gflags from GitHub, enters `/rocksdb`, cleans, builds the static Java artifact, and copies `librocksdbjni-*` plus `rocksdbjni-*`.

State and persistence behavior: Mutates container package state, `/tmp`, `/usr`, `/rocksdb/java/target`, and `/rocksdb-build`. It assumes a disposable build image and removes `/tmp/*` after gflags installation.

Dependencies and integration points: Integrates with cross-build container workflows and Java Makefile/native target `rocksdbjavastatic`. Depends on Alpine package names, OpenJDK 7 path, network access, and `/rocksdb`/`/rocksdb-build` mounts.

Risks and edge cases: Edge repositories and OpenJDK 7 are fragile over time. Building gflags from an old branch can fail if upstream or toolchain assumptions change. `rm -rf /tmp/*` is broad but likely acceptable only inside a dedicated container.

Test signals: Successful artifact copies into `/rocksdb-build`, `make` completion, and loadable `librocksdbjni` on Alpine/musl-compatible targets indicate success.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux-alpine.sh -->
