# sources/storage-engines/rocksdb/build_tools/make_package.sh

## Purpose
This Bash script builds a RocksDB static library, stages an install tree, and packages it as either a Debian package or RPM using `fpm`. It accepts exactly one argument, the RocksDB version string to pass to the package metadata. In RocksDB's top-level `Makefile`, it is invoked by the package target with the shared major/minor version.

## Important APIs, types, and functions
The script uses Bash functions rather than external APIs. `log` emits `[+]` status lines. `fatal` emits `[!]` and exits non-zero. `platform` detects `centos` from `/etc/yum.conf` or `ubuntu` from `/etc/dpkg/dpkg.cfg`, otherwise exits. `package` installs an OS package only when not already present, using `dpkg --get-selections`/`apt-get install` on Ubuntu and `rpm -qa`/`yum install` on CentOS. `detect_fpm_output` sets exported `FPM_OUTPUT` to `deb` or `rpm`. `gem_install` installs a Ruby gem if `gem list` does not already show it. `main` validates arguments, prepares build dependencies for Vagrant-like environments, builds and stages RocksDB, and invokes `fpm`.

## Control flow
The script enables `set -e`, defines helpers, detects `OS`, detects `FPM_OUTPUT`, and then calls `main "$@"` with shellcheck suppression for unquoted argument expansion.

`main` first requires exactly one version argument. When `/vagrant` exists, it assumes a Vagrant packaging VM and installs compiler, gflags, Ruby, and RPM build prerequisites. Ubuntu Vagrant installs `g++-4.8`, exports `CXX=g++-4.8`, installs `libgflags-dev`, and installs `ruby-all-dev`. CentOS Vagrant installs the devtools 1.1 repo when missing, installs GCC/G++ from that repo, exports `CC`, `CPP`, `CXX`, and extends `PATH`, installs a gflags RPM directly if needed, and installs Ruby, Ruby headers, RubyGems, and `rpm-build`.

After VM-specific dependency setup, it ensures the `fpm` gem is installed, runs `make static_lib`, chooses `LIBDIR=/usr/lib` for Debian-style packages or `rpm --eval '%_libdir'` for RPMs, removes any existing `package` staging directory, runs `make install DESTDIR=package PREFIX=/usr LIBDIR=$LIBDIR`, and finally calls `fpm -s dir -t $FPM_OUTPUT -C package -n rocksdb -v <version>` with URL, maintainer, license, vendor, description, and the staged `usr` tree.

## State and persistence behavior
The script mutates the working tree by deleting and recreating the `package` staging directory. It also produces package artifacts in the current directory through `fpm`. On Vagrant images it mutates system package state via `apt-get`, `yum`, `rpm -i`, `gem install`, and possibly downloads `/etc/yum.repos.d/devtools-1.1.repo`. Environment variables exported by the script include `OS`, `FPM_OUTPUT`, and compiler-related variables for old Ubuntu/CentOS build environments.

## Dependencies and integration points
The script depends on Bash, `make`, the RocksDB Makefile's `static_lib` and `install` targets, RubyGems, `fpm`, OS package managers, and platform-specific package metadata tools. It integrates with the top-level RocksDB package target and uses the source tree's normal install rules to decide what gets packaged. It assumes package output type from distro detection rather than from a command-line option.

## Risks and edge cases
The script likely requires root privileges for package installation inside Vagrant, but it does not use `sudo`; callers must already have permissions. OS detection is coarse and misses modern derivatives or container images that do not have `/etc/yum.conf` or `/etc/dpkg/dpkg.cfg`. The fatal message for unknown OS contains a typo, but still exits.

Package/gem existence checks use simple `grep --quiet $1` patterns and unquoted variables, so package names that are substrings of other packages or contain regex metacharacters can produce false positives. The direct CentOS gflags RPM URL and devtools repo URL are historical external dependencies and may no longer be reachable. `gem list | grep` can also match unintended gems.

`rm -rf package` is intentional but destructive if a caller expected to preserve a local `package` directory. `set -e` catches most command failures, but the script does not trap cleanup or provide partial-state recovery. It builds `static_lib`, so package contents are limited by what `make install` installs from that build mode.

## Test signals
Basic validation is `bash -n build_tools/make_package.sh` and ShellCheck-style review, though the file already suppresses specific shellcheck findings. Functional validation requires a packaging VM or container matching Ubuntu or CentOS, a successful `make static_lib`, a successful staged `make install`, and a generated `.deb` or `.rpm` with the expected version and installed `usr` payload. Integration validation is the top-level `make package` target.
