# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.expected.conf

## Purpose

This file is the non-optimized expected canonical output for the Xen target fixture. It captures how checkpolicy decompiles the Xen-specific source policy after binary serialization.

## Important Semantics

The expected output emits `sid xen` instead of the source's `sid kernel`, preserves `dom0` and `domio`, expands type aliases and set-based rules, emits optional rules concretely, rewrites `sameuser` in `validatetrans`, normalizes role transition without an explicit class to `process`, and prints Xen hardware contexts with hexadecimal values for iomem/ioport/pcidevice ranges.

The non-optimized output retains the `BOOL1` conditional as an empty true branch and a false branch granting `PERM1`.

## Control Flow And Integration

`test_roundtrip.sh` uses this artifact for the `--target xen -c 30 -E` lane and verifies both source-to-expected and expected-to-expected round trips.

## State And Persistence

The file is a canonical snapshot of Xen-target policy state and target-specific context records. It represents the binary policy's output form rather than the exact authoring syntax.

## Dependencies And Risks

It is sensitive to target-specific SID mapping and numeric formatting. Any update to Xen policy support can require expected-file updates; unrelated diffs in general TE sections may indicate shared checkpolicy regressions.

## Test Signals

Passing diffs validate Xen SIDs, device contexts, class and type declarations, AV and TE rules, conditional rendering, role/user sections, constraints, and validatetrans canonicalization.
