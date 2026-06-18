# sources/security-integrity/selinux/checkpolicy/tests/policy_minimal_mls.conf

## Purpose

`policy_minimal_mls.conf` is the smallest MLS policy fixture in this subset. It extends the minimal non-MLS policy with one sensitivity, dominance declaration, category, level, MLS constraint, user MLS range, and SID MLS range.

## Control Flow And Integration

The round-trip script compiles/decompiles it with `-M -E` and with `-M -E -S -O`, using the file itself as the expected output. No optimizer or canonical text changes are expected.

## State And Persistence

The persisted policy includes a minimal MLS lattice (`s0`, `c0`, `s0:c0`), an MLS constraint on `CLASS1 PERM1`, and contexts normalized in the source as `s0 - s0` ranges. The type/role/user state mirrors the non-MLS minimal fixture.

## Dependencies And Risks

This is a smoke test for MLS parser enablement and minimum valid MLS policy structure. It does not cover MLS aliases, range transitions, category sets beyond one category, or complex constraints.

## Test Signals

Exact identity after both MLS round-trip lanes confirms that basic MLS declarations, constraints, and contexts survive binary serialization without unexpected formatting changes.
