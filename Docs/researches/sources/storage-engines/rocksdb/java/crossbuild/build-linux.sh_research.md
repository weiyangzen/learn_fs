<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux.sh -->
# Research: sources/storage-engines/rocksdb/java/crossbuild/build-linux.sh

Purpose: Provides a simple Debian/Ubuntu-style Linux build script for RocksDB Java artifacts and powers down the VM when complete.

Important APIs/types/functions: Uses `apt-get`, installs compiler and compression dependencies, sets `JAVA_HOME` to `java-7-openjdk*`, runs `make jclean clean`, `make -j 4 rocksdbjavastatic`, copies artifacts to `/rocksdb-build`, and calls `sudo shutdown -h now`.

Control flow: Install packages, select Java home, enter `/rocksdb`, clean, build static Java artifacts, copy native libraries/JARs, then halt the machine.

State and persistence behavior: Mutates host package state and build output directories. The final shutdown is a strong side effect indicating this script is designed for ephemeral VM automation rather than interactive use.

Dependencies and integration points: Depends on apt repositories, default JDK/OpenJDK 7 path, Makefile native Java build target, `/rocksdb` source mount, and `/rocksdb-build` artifact mount.

Risks and edge cases: OpenJDK 7 path/package availability is unlikely on modern distributions. The unconditional shutdown is hazardous outside a dedicated build VM. No `set -e` means early failures may not stop later copy/shutdown commands.

Test signals: Presence of copied `librocksdbjni-*` and `rocksdbjni-*` in `/rocksdb-build`, plus VM lifecycle logs showing clean shutdown after a successful build.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/crossbuild/build-linux.sh -->
