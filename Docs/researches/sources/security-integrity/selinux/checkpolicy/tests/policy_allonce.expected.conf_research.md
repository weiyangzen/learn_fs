# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.expected.conf

## Purpose

This file is the canonical decompiled output expected when `policy_allonce.conf` is compiled and then converted back to source without `-S -O` optimization. It captures checkpolicy's normalized representation of the broad non-MLS fixture.

## Important Semantics

The file removes source-only constructs such as `expandattribute` and tunable declarations that do not survive in the same textual form, emits expanded type aliases as separate `typealias` statements, expands type sets into individual `auditallow`, `dontaudit`, and filename transition rules, emits optional `allow TYPE1 self:CLASS2` as a concrete rule, and rewrites `sameuser` to `(u1 == u2)`.

Extended permission ranges are canonicalized into segments, for example the ioctl range from `0x456-0x5678` is split along internal boundaries. Conditional blocks are printed in normalized `if (BOOL)` form, with the `! BOOL1` source becoming an empty true branch and populated `else` branch. Paths and network contexts are normalized: root genfs becomes `"/"`, CIDR node contexts become address/mask pairs, and netif contexts are sorted canonically. InfiniBand pkey hex values are rendered as decimal.

## Control Flow And Integration

`test_roundtrip.sh` first compares this file against decompiled output from `policy_allonce.conf`, then compiles this expected file and decompiles it again to ensure the canonical form is idempotent.

## State And Persistence

This artifact represents persisted binary policy semantics rather than authoring syntax. It intentionally excludes constructs optimized away only by `-S -O`; for example some conditional permissions remain broader here than in the optimized expected file.

## Dependencies And Risks

The file is sensitive to libsepol output ordering, xperm range formatting, condition simplification, and canonical address formatting. Legitimate compiler changes require synchronized updates to this expected file and `policy_allonce.expected_opt.conf`; otherwise the round-trip test will fail even if policy semantics remain equivalent.

## Test Signals

A passing diff confirms broad non-MLS parser/decompiler stability, including type/role/user sections, AV rules, xperms, conditional rules, constraints, SID contexts, filesystem contexts, network contexts, and InfiniBand contexts.
