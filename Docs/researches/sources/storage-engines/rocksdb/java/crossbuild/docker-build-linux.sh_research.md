<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/docker-build-linux.sh -->
# Research: sources/storage-engines/rocksdb/java/crossbuild/docker-build-linux.sh

Purpose: Builds RocksDB Java Linux artifacts inside Docker from a mounted host checkout, supporting optional software collection toolchains and copying final files to a mounted target directory.

Important APIs/types/functions: Uses environment variable `J`, `/rocksdb-host`, `/rocksdb-local-build`, `/rocksdb-java-target`, `scl --list`, `devtoolset-8/7/2`, `make clean-not-downloaded`, `PORTABLE=1 J=$J make -j$J rocksdbjavastatic`, and copies `.so`, `.jar`, and `.jar.sha1` files.

Control flow: With `set -e`, it defaults `J=1`, creates a local build directory, copies the host tree into it, chooses the newest supported devtoolset if `scl` is available, otherwise uses the system compiler, runs clean/build, and copies Linux Java artifacts to `/rocksdb-java-target`.

State and persistence behavior: It deletes and recreates `/rocksdb-local-build/*` every run and writes artifacts to `/rocksdb-java-target`. The source mount is read and copied, not built in place, reducing host tree mutation.

Dependencies and integration points: Integrates with Docker cross-build images, RocksDB Makefile, and artifact publishing scripts. Depends on mounted paths, toolchain packages, and the target naming convention `java/target/rocksdbjni-*-linux*.jar`.

Risks and edge cases: Copying the entire checkout can be expensive and may include untracked files from the host. If no recognized devtoolset exists the script exits. Artifact glob mismatches fail under `set -e`, which is good for detecting packaging drift.

Test signals: Successful creation of Linux `.so`, `.jar`, and `.jar.sha1` files in `/rocksdb-java-target`, plus build logs showing selected compiler path and parallelism.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/docker-build-linux.sh -->
