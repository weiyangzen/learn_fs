# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.expected_opt.conf

## Purpose

This file is the optimized MLS expected output for `policy_allonce_mls.conf` under `-M -S -O`. It verifies that optimizer behavior remains correct when MLS declarations and ranges are present.

## Important Semantics

It is nearly identical to `policy_allonce_mls.expected.conf`; the intentional optimization difference is in the `BOOL1` false branch, where the redundant `PERM1` permission is removed and only `ioctl` remains because `PERM1` is already granted unconditionally.

## Control Flow And Integration

`test_roundtrip.sh` uses this file in the MLS optimized lane and then verifies it is itself stable under repeated compile/decompile with the same options.

## State And Persistence

The file persists canonical MLS policy state plus optimizer-pruned conditional permission state. It should not alter MLS lattice declarations, ranges, SIDs, or context forms relative to the non-optimized expected file except where optimization changes effective rule output.

## Dependencies And Risks

The main risk is over-pruning conditional permissions in an MLS policy or accidentally changing MLS formatting while touching optimizer code. Because only one line differs from the non-optimized MLS expected file, unexpected wider diffs are high-value regression signals.

## Test Signals

Passing tests confirm that `-S -O` removes redundant conditional permissions without disturbing MLS declarations, range transitions, or context canonicalization.
