# sources/storage-engines/rocksdb/build_tools/setup_centos7.sh

## Purpose
This Bash provisioning script configures a CentOS 7 style host, apparently a Vagrant environment, to build and smoke-test RocksDB 6.7.3 with compression dependencies. It installs system packages, builds zstd 1.4.4 from source, expands RocksDB into `/usr/local`, and compiles the static library plus examples.

## Important APIs, functions, and control flow
The script is linear and uses `set -ex`, so every command is echoed and any failing command terminates the run. It declares `ROCKSDB_VERSION` and `ZSTD_VERSION`, updates yum, installs EPEL and packages such as `gcc-c++`, `snappy-devel`, `zlib-devel`, `bzip2-devel`, `lz4-devel`, `libasan`, and `gflags`, then creates `/usr/local/rocksdb-${ROCKSDB_VERSION}` and symlinks `/usr/local/rocksdb`. It downloads GitHub release tarballs into `/tmp`, builds zstd with `make && make install`, changes ownership of the RocksDB tree to `vagrant:vagrant`, runs `sudo -u vagrant make static_lib`, builds examples, and runs `c_simple_example`.

## State, persistence, and dependencies
Persistent state is installed into system package databases, `/usr/local/lib`, `/usr/local/rocksdb-*`, and the `/usr/local/rocksdb` symlink. It assumes yum, internet access to GitHub, `sudo`, a `vagrant` user, and write access to `/usr/local` and `/tmp`. It also assumes RocksDB 6.7.3 still builds with the installed CentOS toolchain and the manually installed zstd.

## Integration points
This is not used by cache runtime code; it is a build/bootstrap utility for older CentOS environments. It integrates with RocksDB's make build, examples directory, and system dynamic library path through `LD_LIBRARY_PATH=/usr/local/lib/` for examples.

## Risks and test signals
The hard-coded versions are old, GitHub download URLs are mutable network dependencies, and the `vagrant` user assumption makes the script unsuitable for generic CentOS hosts without edits. `ln -sfT` and `chown -R` affect global `/usr/local` state. A successful smoke signal is completion of `make static_lib`, `make all` in `examples/`, and `./c_simple_example` under the `vagrant` account.
