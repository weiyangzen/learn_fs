# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/tests/test_add_rule.py

## Purpose
Pytest-based parser/serialization tests for `ipfw add` rule compilation, validating the exact ioctl/TLV byte structures emitted by `/sbin/ipfw`.

## Main Responsibilities
- Builds expected `IpFwXRule` structures using Python helper classes.
- Runs `ipfw` through `DebugIoReader` to capture generated ioctl records.
- Compares expected and actual byte output.
- Provides recursive object-diff printing to diagnose mismatched TLV/insn trees.

## Key Test Coverage
- Rule numbers and basic accept rules.
- IPv4/IPv6 zero-mask simplification.
- OR address blocks.
- Table references and table lookups.
- Lookup masks for mark, MAC, IPv4, jail, and IPv6 fields.
- Table value checks for legacy, NAT, NH4, and NH6 values.
- Comments.
- External actions such as `tcp-setmss` and `nptv6`.
- Stateful rule constructs: `check-state`, `keep-state`, and `record-state`.
- Action compilation for allow/accept/deny/reject/reset/unreach/count/queue/pipe/skipto/netgraph/divert/tee/call/setdscp/reass/return.
- Single instructions such as `prob`, protocol, and port matching.
- Source and destination port range compilation.

## Key Implementation Details
- `compile_rule()` wraps expected instructions in `CTlvRule` and optional object-name TLVs.
- `verify_rule()` asserts exactly one ioctl request is generated.
- `differ()` recursively compares object byte representations and prints missing/extra/different objects.

## Integration Points
Imports support from `atf_python.sys.netpfil.ipfw`, including instruction, ioctl, enum, and utility classes.

## Notable Edge Cases
- Some imports are broad because the test suite constructs many instruction variants.
- One `setfib` case is skipped because it depends on `net.fibs > 1`.
