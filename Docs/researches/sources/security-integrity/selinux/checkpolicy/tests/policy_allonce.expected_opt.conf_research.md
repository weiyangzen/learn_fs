# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.expected_opt.conf

## Purpose

This file is the expected canonical output for `policy_allonce.conf` when the policy is compiled and decompiled with `-S -O`. It validates the optimizer's effect on the same broad non-MLS grammar fixture.

## Important Semantics

Most content mirrors `policy_allonce.expected.conf`, but the optimized conditional bodies are pruned. In the `BOOL1` false branch, the unconditional `allow TYPE1 self:CLASS1 { PERM1 }` already grants `PERM1`, so the optimized branch keeps only `ioctl`. In the `BOOL2` branch, the unconditional xperm already includes `0x1`, so the branch keeps only `0x2`.

## Control Flow And Integration

`test_roundtrip.sh` uses this file for the `check_policy policy_allonce.conf policy_allonce.expected_opt.conf '-S -O'` lane, then verifies the expected file itself is stable under the same options.

## State And Persistence

The file represents the optimized persisted semantics of the compiled policy, not the original source form. Its main state signal is removal of redundant conditional permissions while preserving nonredundant rules, declarations, contexts, and constraints.

## Dependencies And Risks

The artifact is tightly coupled to optimizer logic. Changes in redundancy detection for normal permissions or extended permissions will surface as small but meaningful diffs. A risk is treating an optimizer diff as formatting-only; in this file the reduced permissions are the main test oracle.

## Test Signals

The strongest signal is the small diff from the non-optimized expected file: only redundant conditional permissions should disappear. Broader changes suggest unintended parser/decompiler or optimizer behavior.
