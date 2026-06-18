# sources/security-integrity/selinux/libsepol/cil/src/cil_find.h

## Purpose
`cil_find.h` exposes the AST AV-rule search helper and class expansion helper used by deny handling, neverallow verification, and policy serialization.

## Important APIs, Types, And Functions
`cil_find_matching_avrule_in_ast` searches an AST subtree for AV or extended AV rules that overlap a target rule. `cil_expand_class` converts a normal class or map class into a list of concrete classes.

## Control Flow
The header has no runtime flow. The implementation performs tree walking and recursive class-permission expansion.

## State And Persistence Behavior
No state is stored in the header. Callers of `cil_expand_class` receive a newly allocated `struct cil_list` and must destroy it without destroying class data.

## Dependencies And Integration Points
It includes `cil_flavor.h`, `cil_tree.h`, and `cil_list.h`, tying the API to AST node flavors and CIL list ownership. `cil_deny.c`, `cil_policy.c`, and `cil_binary.c` are the main consumers.

## Risks And Edge Cases
The API returns matching nodes by appending to a caller-owned list, so callers must initialize and clean that list. The `match_self` flag changes whether the target can match itself, which is important for neverallow checks versus deny rewrites.

## Test Signals
Compile tests catch signature drift. Behavioral tests should verify that callers destroy expanded class lists and that self-matching behavior differs as expected between rule-search contexts.
