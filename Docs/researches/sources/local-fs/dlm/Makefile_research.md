# File Research: sources/local-fs/dlm/Makefile

## Purpose
Top-level build, cleanup, tarball, and RPM entry point for the DLM userspace source tree. It delegates normal build targets to `libdlm`, `dlm_controld`, `dlm_tool`, and `fence`, then handles release metadata generation and RPM packaging.

## Main Behavior
- `all install clean` loops through subdirectories and runs the same make target in each.
- The delegated targets also remove generated packaging artifacts, including `dlm.spec`, tarballs, rpm output directories, and `.version` when in a git checkout.
- `.version` is generated only inside a git repository. It derives `relver` from the latest `dlm-*` tag, counts commits since that tag, records the short commit id as `alphatag`, and stores an RPM changelog date.
- `dlm.spec` is rendered from `dlm.spec.in` using `.version` values; when building from a release tarball without `.git`, it strips `%global numcomm` and `%global alphatag`.
- `tarball` creates `dlm-$tarver.tar.gz`, using plain release version for release builds and `relver.numcomm.alphatag` for non-release git builds.
- `srpm` and `rpm` run `rpmbuild` with all rpm build directories redirected to the current source directory.

## Integration Points
- Consumes `include/version.cf`, `.git` metadata, and `dlm.spec.in`.
- Produces `.version`, `dlm.spec`, source tarballs, SRPMs, and binary RPMs.
- Assumes subdirectories have compatible `all`, `install`, and `clean` targets.

## Risks and Notes
- Build orchestration is serial and shell-loop based; one failing subdirectory stops the whole target through `set -e`.
- `.version` cannot be regenerated from a release tarball, so cleanup intentionally preserves it outside git.
- `tar --transform "s/^./dlm-$$relver/"` prefixes archive paths with the release version, not the non-release `tarver`, which is worth preserving for compatibility with the generated spec.
