# File Research: sources/local-fs/linux-apfs-rw/genver.sh

This shell script generates `version.h` for the kernel module build.

Behavior:
- If `git` is available and `.git` exists, it sets `GIT_COMMIT` from `git describe HEAD | tail -c 9`.
- Otherwise, it reads `PACKAGE_VERSION` from `dkms.conf` and appends `?`.
- It writes `#define GIT_COMMIT "<value>"` to `version.h`.

Research relevance: this is build metadata generation. It gives the module a compile-time version/commit string, with DKMS package version fallback outside a git checkout.
