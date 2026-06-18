<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux-centos.sh -->
# Research: sources/storage-engines/rocksdb/java/crossbuild/build-linux-centos.sh

Purpose: Builds portable RocksDB Java artifacts on CentOS using old-toolchain compatibility packages and copies outputs to `/rocksdb-build`.

Important APIs/types/functions: Uses `yum`, EPEL, `cmake3` alternatives, `devtoolset-2`, gflags v2.0 source build, `JAVA_HOME=/usr/lib/jvm/java-1.7.0`, `scl enable devtoolset-2`, `make clean-not-downloaded`, and `PORTABLE=1 make -j8 rocksdbjavastatic`.

Control flow: The script removes a fixed `releasever` override, installs dependencies, configures CMake alternatives, enables an older GCC toolchain, downloads/builds gflags, sets Java and library paths, then runs clean/build targets under the software collection and copies native/JAR outputs.

State and persistence behavior: Mutates system package repositories, alternatives, `/usr/local`, current gflags source directory, `/rocksdb/java/target`, and `/rocksdb-build`. It is intended for disposable build images.

Dependencies and integration points: Depends on CentOS yum repositories, `people.centos.org` devtools repo, OpenJDK 7, gflags source archive, and Makefile `rocksdbjavastatic`. It supports legacy Linux binary compatibility for Java artifacts.

Risks and edge cases: The devtools-2 repo and Java 7 are obsolete and likely brittle. `sudo` is required inside the environment. The comment has typos but the operational risk is external repo availability and old compiler/library ABI expectations.

Test signals: Build success under `scl`, artifact copies to `/rocksdb-build`, and later JNI loading/tests on target CentOS-compatible systems.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux-centos.sh -->
