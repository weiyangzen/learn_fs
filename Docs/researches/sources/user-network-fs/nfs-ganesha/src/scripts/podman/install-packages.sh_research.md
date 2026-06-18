<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/podman/install-packages.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/podman/install-packages.sh

## Purpose
This shell script installs NFS-Ganesha build dependencies inside supported container base images. It is used by the Podman `Containerfile` rather than by normal runtime deployments, and it encodes per-family package-manager logic for Debian/Ubuntu, Red Hat-family images, Fedora, and SUSE/SLE.

## Important APIs, Types, and Functions
The script is function-oriented: `install_debian`, `install_rh`, and `install_suse` perform package installation for their release families. After sourcing `/etc/os-release`, a `case` maps `ID` to a `family` name and invokes `"install_${family}"`. Package-variable knobs include `libnsl_pkg`, `python3_distutils`, `python_pkg`, and `extra_repos`, which account for distro-version differences.

## Control Flow
For Debian-family systems the script sets `DEBIAN_FRONTEND=noninteractive`, runs `apt-get update`, suppresses `libnsl-dev` on older Debian/Ubuntu variants, suppresses `python3-distutils` on Ubuntu 24.04, then installs compilers, CMake, Doxygen, ACL/cap/dbus/krb5/jemalloc/urcu development packages, Python, Qt tools, rsync, sudo, and UUID headers. For Red Hat-family systems it patches CentOS 8 mirror URLs, installs EPEL except on Fedora, enables `powertools`, `crb`, or `devel` repositories as needed, and installs development tools plus equivalent libraries. SUSE installs the `devel_basis` pattern and explicit development packages via `zypper`.

## State and Persistence Behavior
The script mutates the container image filesystem by installing packages and may edit `/etc/yum.repos.d/CentOS-*` for CentOS 8. It does not persist repository state outside the container build context. Package-manager caches and enabled repositories become part of the resulting image layer.

## Dependencies and Integration Points
It depends on the package managers and release metadata available in the base image: `apt-get`, `yum`/DNF compatibility tools, or `zypper`, plus `/etc/os-release`. It is tightly coupled to `ganesha-container`, which constrains the distro versions before building. The installed dependency set feeds CMake builds, documentation generation, Qt-based tooling, and sanitizer-linked builds.

## Risks and Test Signals
Risks include package name drift, missing repositories in minimal images, CentOS 8 vault assumptions becoming stale, Fedora packages diverging from RHEL names, SLE library version changes such as `libasan4`, and intentionally empty package variables relying on unquoted expansion. Test signals are successful container builds for every supported distro/version, CMake configure success inside each image, and smoke builds using DBus, Kerberos, jemalloc, ACL, UUID, and URCU headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/podman/install-packages.sh -->
