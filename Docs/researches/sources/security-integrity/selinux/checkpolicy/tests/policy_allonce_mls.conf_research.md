# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.conf

## Purpose

`policy_allonce_mls.conf` is the MLS counterpart to the broad all-in-one checkpolicy fixture. It exercises MLS declarations and range handling while still covering many of the same type, role, conditional, context, and xperm constructs as the non-MLS fixture.

## Policy Surface

The MLS-specific surface includes sensitivities, a sensitivity alias, dominance, categories with aliases, levels, `mlsconstrain`, `mlsvalidatetrans`, users with level/range, SID contexts with ranges, MLS ranges on `fs_use_*`, genfs, port, netif, node, InfiniBand pkey, and InfiniBand endport contexts, and a `range_transition`.

The non-MLS-style surface includes classes, common permissions, default rules, `policycap open_perms`, attributes, type aliases, typebounds, booleans and tunables, AV/TE rules, xperms, permissive and neveraudit declarations, roles, role transitions, optional rules, constraints, and validatetrans.

## Control Flow And Integration

The fixture is compiled by `test_roundtrip.sh` with `-M` for the standard MLS expected output and with `-M -S -O` for the optimized expected output. Its declaration choices are designed to expose MLS canonicalization rather than runtime flow.

## State And Persistence

The compiled binary policy must persist MLS lattice declarations, aliases, category ranges, and security contexts. The expected output verifies that shorthand ranges are expanded to canonical low-high forms such as `s0 - s0`, aliases like `CATALIAS` resolve to canonical categories, and `range_transition` prints as a low-high MLS range.

## Dependencies And Risks

This file is sensitive to the checkpolicy MLS parser and decompiler. Because it combines MLS and non-MLS constructs, failures can come from general TE formatting or MLS-specific formatting. Alias handling and range formatting are particularly fragile compatibility points.

## Test Signals

Passing tests confirm MLS declaration parsing, constraint formatting, alias resolution in dominance and categories, MLS context normalization for SIDs and labeling statements, xperm formatting, conditional rule handling, and optimized removal of redundant permissions in the `_expected_opt` lane.
