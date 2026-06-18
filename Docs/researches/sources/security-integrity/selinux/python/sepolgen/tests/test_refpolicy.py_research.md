# sources/security-integrity/selinux/python/sepolgen/tests/test_refpolicy.py

## Purpose
This file tests core reference-policy model objects: identifier sets, extended permission sets, SELinux security contexts, object classes, AV rules, extended AV rules, type rules, parse tree nodes, and headers iteration.

## Important Tests And Exercised APIs
`TestIdSet` verifies compact versus braced space string formatting. `TestXpermSet` validates initialization, private range normalization, add/extend merging, complement formatting, single values, multi-values, and ranges. `TestSecurityContext` validates context parsing, MLS default behavior via `selinux.is_selinux_mls_enabled()`, explicit default levels, invalid context handling, and equality.

`TestObjectClass`, `TestAVRule`, `TestAVExtRule`, and `TestTypeRule` validate model initialization and string serialization. `AVExtRule.from_av()` is tested for normal target and self-target conversion. `TestParseNode` constructs a small tree but does not assert traversal output. `TestHeaders` checks iteration over all children and only interfaces.

## Control Flow
Tests mostly instantiate model objects, mutate public sets/fields, call formatting or conversion methods, and assert exact strings or object fields. Some set-order-sensitive checks are normalized by splitting and sorting.

## State And Persistence
All state is in memory. One test consults live SELinux MLS state through the `selinux` Python binding, making expected context string output environment-sensitive.

## Dependencies And Integration Points
It depends on `sepolgen.refpolicy`, `sepolgen.access`, and the external `selinux` Python module. The tested objects are central integration points for access parsing, policy generation, interface expansion, and audit conversion.

## Risks And Edge Cases
`TestParseNode.test_walktree()` lacks assertions and is currently only a construction smoke test. Some serialization expectations depend on set formatting implementation. Environment-dependent MLS behavior can produce different expected strings depending on the host SELinux configuration.

## Test Signals
This is a broad unit signal for the policy model layer, especially xperm range normalization and rule string generation. It does not deeply validate tree walking semantics despite constructing parse nodes.
