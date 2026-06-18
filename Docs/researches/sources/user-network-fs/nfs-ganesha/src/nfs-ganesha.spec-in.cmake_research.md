<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/nfs-ganesha.spec-in.cmake -->
# sources/user-network-fs/nfs-ganesha/src/nfs-ganesha.spec-in.cmake

## Purpose
This is the CMake-templated RPM spec for packaging NFS-Ganesha and its optional FSALs, utilities, monitoring module, tracing library, embedded ntirpc, SELinux policy, service units, configs, and admin tooling.

## Important APIs, Types, and Functions
Important RPM/CMake constructs include `%define`, `%global`, `%bcond` placeholders such as `@BCOND_GPFS@`, the `on_off_switch()` macro, CMake-substituted versions (`@GANESHA_BASE_VERSION@`, `@GANESHA_EXTRA_VERSION@`, `@NTIRPC_VERSION_EMBED@`, `@CPACK_SOURCE_PACKAGE_FILE_NAME@`), `%package`, `%description`, `%prep`, `%build`, `%install`, scriptlets (`%pre`, `%post`, `%preun`, `%postun`, `%posttrans`), and many `%files` sections.

The spec defines feature toggles for FSALs (`nullfs`, `mem`, `gpfs`, `xfs`, `lustre`, `ceph`, `rgw`, `gluster`, `kvsfs`), protocols/features (`rdma`, `9P`, `nfs_rdma`, `rpc_rdma`, `qos`, `monitoring`, `nfsidmap`, `rpcbind`, unwind/enriched backtrace, LTTng, RADOS features, admin tools, GUI tools, man pages, sanitizers, allocators, legacy Python install, system ntirpc, and MSPAC).

## Control Flow
At RPM parse time, distro conditionals select BuildRequires/Requires for SUSE, Fedora, RHEL, Python, SELinux, rpcbind/portmap, system ntirpc, and optional packages. `%build` runs `cmake3` with feature toggles translated into `-DUSE_*` and related options, then retries `make` up to three times. SELinux policy is built for Fedora/RHEL platforms that support it.

`%install` creates config, dbus, sysconfig, logrotate, binary, library, log, libexec, and systemd directories; installs sample configs and service files conditionally; runs `make DESTDIR=%{buildroot} install`; installs SELinux policy artifacts; and removes unwanted Python site-package files. Scriptlets create the `ganesha` user/group, register systemd services, set SELinux log fcontexts, reload dbus, and handle service uninstall/restart macros.

`%files` sections assign installed artifacts to the base package and subpackages, including optional FSAL shared objects, configs, man pages, utilities, monitoring libraries, LTTng libraries, SELinux policy, and embedded libntirpc packages when not using system ntirpc.

## State and Persistence Behavior
The spec persists build choices into the RPM build output and installed system state. Installed persistent paths include `/etc/ganesha`, dbus policy, sysconfig, logrotate config, systemd units/drop-ins, `/var/log/ganesha`, FSAL shared libraries under `%{_libdir}/ganesha`, libraries under `%{_libdir}`, libexec scripts, and optional Python/admin tools. Scriptlets persist the `ganesha` system user/group and SELinux fcontext/module state.

## Dependencies and Integration Points
It integrates CMake build options with RPM subpackage topology. It depends on distro RPM macros, systemd macros, optional SUSE service macros, SELinux macros, compiler/build tools, dbus, libcap, blkid, uuid, userspace RCU, Kerberos, nfs-utils, libattr/libacl, optional backend libraries, optional Python/Sphinx/PyQt tooling, optional proc/monitoring libraries via build outputs, and optional embedded ntirpc packaging.

The monitoring toggle creates an `nfs-ganesha-monitoring` package requiring/providing monitoring libraries. The base package depends on that subpackage when `%{with monitoring}`. Service integration installs `nfs-ganesha.service`, `nfs-ganesha-lock.service`, and `nfs-ganesha-config.service`.

## Risks and Edge Cases
The spec is highly conditional and sensitive to distro macro differences. Some conditionals reference features that are not visibly declared in the reviewed top section, such as `%{with pt}`, so template generation must supply all expected bconds. `%define _unpackaged_files_terminate_build 0` can hide packaging omissions. Retrying `make` can mask flaky parallel build dependencies instead of failing deterministically.

The base package requires `nfs-ganesha-selinux` on Fedora >= 30/RHEL >= 8, so SELinux package build failures affect base installability. Python cleanup removes broad site-package paths and must stay aligned with tool installation layouts. Monitoring `%files` includes `libntirpcmonitoring*`; packaging must ensure this artifact exists only when expected. Scriptlets call `killall -SIGHUP dbus-daemon` and SELinux tools opportunistically, which can behave differently across minimal systems.

## Test Signals
Packaging tests should build RPMs across supported distro macro sets and representative feature combinations: default, monitoring, system vs embedded ntirpc, each FSAL family, utils/gui utils, SELinux platforms, and man-page builds. Install/upgrade/remove tests should verify user/group creation, systemd macro behavior, dbus reload, log directory ownership, config marked `noreplace`, and that every installed file is in the intended subpackage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/nfs-ganesha.spec-in.cmake -->
