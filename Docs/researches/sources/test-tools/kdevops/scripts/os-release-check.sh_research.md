# sources/test-tools/kdevops/scripts/os-release-check.sh

## Purpose
Reports whether the current host matches a requested Linux distribution family, using `/etc/os-release`.

## Important APIs
`check_distro(arg)` dispatches supported names. `check_distro_redhat()`, `check_distro_suse()`, and `check_distro_ubuntu()` grep `/etc/os-release` for family-specific identifiers and print `y` or `n`.

## Control flow
The script requires one distribution argument. If `/etc/os-release` is missing it prints `n` and exits 0. Unsupported distro names also produce `n`.

## State and dependencies
Read-only. Depends on `/etc/os-release`, `grep`, and shell conditionals. It is likely used from Make/Kconfig glue that expects single-character boolean output.

## Integration points
Useful for conditional package/install logic where the caller wants Red Hat, SUSE, or Ubuntu family detection without parsing the file directly.

## Risks and test signals
Matching is simple substring grep and can be sensitive to case or future `os-release` formatting. It returns success status even for `n`, so callers must read stdout. Test with fixture files or container images for each distro family.
