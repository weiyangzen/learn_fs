# File Research: sources/os/bsd/netbsd-src/lib/bumpversion

Shell maintenance script for updating `shlib_version` files. It supports `-c` to create missing version files, `-m` to bump the major version and reset minor to zero, and `-n` dry-run mode.

For each directory argument it validates `shlib_version`, sources `major` and `minor`, computes the new version, and either writes `major=<n>` / `minor=<n>` via a temporary file or reports the prospective change. It exits nonzero if any directory or version file check fails.
