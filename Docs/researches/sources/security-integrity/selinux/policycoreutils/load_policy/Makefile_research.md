<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/load_policy/Makefile -->
# sources/security-integrity/selinux/policycoreutils/load_policy/Makefile

## Purpose

Builds and installs `load_policy`. The source was read completely for this report (32 lines).

## Important APIs, Types, and Functions

Adds libselinux include/library paths, NLS defines, links libselinux and libsepol, installs binary and man8 pages, supports localized manpages and relabel.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/load_policy/Makefile -->
