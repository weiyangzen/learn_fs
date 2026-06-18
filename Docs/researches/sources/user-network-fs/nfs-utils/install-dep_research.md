# sources/user-network-fs/nfs-utils/install-dep

Purpose: `install-dep` is a convenience script that installs build dependencies for nfs-utils on common Linux distributions.

Important behavior: it detects package managers with `command -v` and runs package installation for dnf/yum-family, apt-family, or zypper-family systems. Packages include Autotools, libtool, make/gcc, rpcgen, libtirpc, libevent, sqlite, device-mapper, blkid, Kerberos, keyutils, uuid, and related development headers.

Control flow: each package-manager block is independent; on unusual systems with multiple package managers, more than one block could run. The dnf/yum detection uses shell operator precedence: `command -v dnf >/dev/null || command -v yum >/dev/null && { yum install ...; }`, so it actually invokes `yum` in the block even when only `dnf` was detected.

State and persistence: it modifies the host package database and installs system packages. It does not write repo files.

Dependencies and integration points: depends on root privileges and the target package manager. It supports building source configured by `configure.ac`.

Risks: package installs are non-idempotent but generally safe; they require network and privileges. The dnf/yum logic likely should call the detected tool rather than hard-coded `yum`. Apt uses `--ignore-missing`, which can hide missing dependencies.

Test signals: run in clean containers for Fedora/RHEL, Debian/Ubuntu, and openSUSE; verify each package list satisfies `./autogen.sh && ./configure` for desired feature sets.
