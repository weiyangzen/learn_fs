# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/tests/ipfw_test.sh

## Purpose
Provides an ATF shell integration test for NPTv6 command behavior inside a vnet jail.

## Main Responsibilities
- Creates a vnet jail with an epair interface.
- Loads/requires `ipfw_nptv6`.
- Exercises valid NPTv6 create/list/destroy forms.
- Verifies invalid forms fail and leave no NPTv6 instances behind.

## Key Test Coverage
Valid cases:
- `int_prefix`, `ext_prefix`, and explicit `prefixlen`.
- Dynamic external prefix via `ext_if`.
- Prefixes with embedded `/64` plus explicit `prefixlen`.
- Deprecated embedded prefix length inference, checking warning output.

Invalid cases:
- Supplying both `ext_prefix` and `ext_if`.
- Mismatched embedded prefix lengths.
- Mismatched explicit `prefixlen`.

## Integration Points
- Sources `vnet.subr`.
- Uses `atf_check`, `jexec`, `ifconfig`, and `ipfw nptv6`.
- Requires root and `ipfw_nptv6`.
