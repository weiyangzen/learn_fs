# File Research: sources/os/bsd/freebsd-src/sbin/sysctl/tests/sysctl_test.sh

## Purpose
ATF regression tests for basic `sysctl` output modes and all-node traversal.

## Main Elements
- Uses stable `kern.ostype` expectations: name `kern.ostype`, value `FreeBSD`, type `string`, description `Operating system type`.
- `sysctl_aflag` runs `sysctl -ao` and fails on nonzero exit or stderr.
- `sysctl_aflag_jail` repeats `sysctl -ao` in non-vnet and vnet jails; requires root.
- Tests normal name output, `-n`, `-e`, `-t`, `-d`, `-t -d`, `-d -t`, and `-n -t -d`.
- Registers all cases in `atf_init_test_cases()`.

## Dependencies And Integration
Requires `/usr/sbin/sysctl`, ATF helpers, and root/jail support for the jail case.

## Risk Notes
The all-node tests intentionally avoid `atf_check` output capture because `sysctl -ao` can generate large output.
