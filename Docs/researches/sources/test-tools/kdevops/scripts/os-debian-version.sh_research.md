# sources/test-tools/kdevops/scripts/os-debian-version.sh

## Purpose
Checks whether `/etc/debian_version` contains a requested Debian version/distribution string.

## Important APIs and control flow
`check_debian_version(pattern)` greps `DEBIAN_VERSION_FILE=/etc/debian_version` case-insensitively for the first positional argument, prints `y` on match and `n` otherwise. If the file is absent it prints `n` and exits. The function is invoked immediately at the end of the script.

## State, dependencies, and integration
The script is read-only and depends on `/etc/debian_version` and `grep`. It is suitable for kdevops distro/version checks that expect boolean stdout.

## Risks and test signals
It has no argument validation, so an empty pattern may match unexpectedly depending on grep behavior. It exits with status 0 for both `y` and `n`, so callers must read stdout. Test by probing known version substrings and non-matching strings on Debian-derived and non-Debian hosts.
