# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/pfctl_test.c

## Purpose
ATF C harness for pfctl parser/output regression tests.

## Main Elements
- Reads expected output files and command output into `sbuf`s.
- Runs `pfctl -o none -nvf` against each input file and compares to `.ok` output, or regex-matches `.fail` for expected failures.
- Runs selfpf tests by feeding expected normalized output back through pfctl.
- Provides helpers to create/destroy VLAN interfaces for interface translation tests inside vnet jails.
- Uses macros from `pfctl_test_list.inc` to instantiate and register many ATF test cases.

## Dependencies And Integration
Uses ATF C API, `posix_spawnp()`, `ifconfig`, `pfctl`, `pf` kernel module metadata, `sbuf`, and test data under `tests/files`.

## Risk Notes
The harness redirects child stdout/stderr through pipes and depends on exact output matching. Interface tests require jail/vnet support and cleanup.
