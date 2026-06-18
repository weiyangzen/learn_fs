# File Research: sources/local-fs/dlm/dlm.spec.in

## Purpose
RPM spec template for packaging the DLM userspace daemon, tools, libraries, headers, pkg-config metadata, udev rules, man pages, and systemd unit/sysconfig files.

## Main Behavior
- Uses template substitutions for `@relver@`, `@rpmdate@`, `@numcomm@`, and `@alphatag@`.
- Defines package name `dlm`, version from `@relver@`, and release suffixes based on optional commit count and alphatag globals.
- Declares license mix as GPLv2, GPLv2+, and LGPLv2+, with README license breakdown.
- Requires Corosync libraries >= 3.1.0, Pacemaker development libraries, systemd development headers, kernel headers, gcc, and make.
- `%build` uses `%set_build_flags` and explicitly disables parallelism via `%make_build -j1`.
- `%install` runs `make install` with RPM `_libdir` and `_sbindir`, then installs `init/dlm.service` and `init/dlm.sysconfig`.
- Defines three packages:
  - Main `dlm` package: daemon, tool, stonith helper, man pages, systemd unit, sysconfig.
  - `dlm-lib`: shared runtime libraries and udev rules.
  - `dlm-devel`: unversioned shared-library links, headers, and pkg-config files.

## Integration Points
- Rendered by the top-level `Makefile`.
- Build uses the repo makefiles directly; upstream has no configure step.
- Runtime dependency links daemon packaging to `corosync`, optional distro kernel module packages, and systemd scriptlets.

## Risks and Notes
- `%make_build -j1` documents that upstream does not support parallel builds.
- Distro conditionals distinguish SUSE/Fedora packaging names.
- Main package requires the exact matching `dlm-lib` version-release.
