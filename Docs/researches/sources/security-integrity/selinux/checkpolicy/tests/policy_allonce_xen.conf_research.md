# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.conf

## Purpose

`policy_allonce_xen.conf` is a Xen-target all-in-one policy fixture. It exercises checkpolicy target-specific handling with Xen SIDs and hardware/device context statements while retaining a representative subset of TE, role, user, conditional, and constraint constructs.

## Policy Surface

The file declares classes, SIDs `kernel`, `dom0`, and `domio`, common permissions, default rules, attributes, types and aliases, booleans/tunables, type transition/member/change rules, allow/audit/dontaudit/neverallow, permissive type, roles and role transitions, conditionals, optional rules, `policycap open_perms`, users, constraints, validatetrans, SID contexts, and Xen-specific `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, and `devicetreecon` statements.

## Control Flow And Integration

The test script compiles it with `--target xen -c 30 -E` and compares the decompiled result to `policy_allonce_xen.expected.conf`; the optimized lane adds `-S -O` and compares with `policy_allonce_xen.expected_opt.conf`.

## State And Persistence

The persisted policy state must translate the source's `sid kernel` into target-specific canonical output `sid xen` in expected files. Numeric hardware ranges are also canonicalized as hexadecimal for iomem, ioport, and pcidevice contexts.

## Dependencies And Risks

This fixture depends on Xen target support in checkpolicy and policy version 30 compatibility. Regressions may appear as SID target name changes, hardware context formatting differences, or optimizer behavior changes in conditional rules.

## Test Signals

Passing tests confirm Xen target parsing, SID canonicalization, hardware context handling, target-compatible TE rule output, conditional output in the non-optimized lane, and complete removal of the redundant `BOOL1` conditional block in the optimized lane.
