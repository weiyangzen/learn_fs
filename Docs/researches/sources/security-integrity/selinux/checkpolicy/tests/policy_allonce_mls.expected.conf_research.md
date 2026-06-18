# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.expected.conf

## Purpose

This file is the canonical decompiled output for `policy_allonce_mls.conf` with MLS enabled and without optimization. It is the oracle for MLS round-trip stability.

## Important Semantics

The expected output resolves `SENSALIAS` in dominance to `s2`, keeps the sensitivity alias declaration, preserves category alias `CATALIAS` while rendering ranges as `c0,c1`, formats `mlsvalidatetrans` with parentheses, expands type aliases and set-based rules, and prints `range_transition TYPE1 TYPE2:CLASS1 s1:c0,c1 - s1:c0,c1`.

MLS contexts are normalized consistently: user ranges become `level s0 range s0 - s1:c0,c1`, SID and fs contexts print canonical ranges, and single-level genfs/port/netif/node/InfiniBand contexts gain `s0 - s0`.

## Control Flow And Integration

`test_roundtrip.sh` compares this file to decompiled output from the source fixture under `-M`, then compiles and decompiles this expected file again to verify idempotence.

## State And Persistence

The file is a persisted semantic snapshot of MLS policy state after binary serialization. It intentionally reflects canonical values rather than original aliases or shorthand syntax where the compiler normalizes those forms.

## Dependencies And Risks

The artifact depends on stable MLS range rendering and rule ordering. Updates to MLS alias resolution, range compression/expansion, or conditional formatting must be reflected here. Small textual diffs can indicate meaningful changes to MLS policy semantics.

## Test Signals

The expected diff validates MLS lattice declarations, MLS constraints, range transitions, canonical MLS contexts, general TE and role/user declarations, and non-optimized conditional branches.
