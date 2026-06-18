# sources/security-integrity/selinux/libsepol/tests/policies/test-linker/small-base.conf

## Purpose
This base fixture drives the linker’s main multi-module tests. It defines global base symbols and optional base blocks that modules can enable.

## Important APIs, Types, And Functions
Important symbols include `enable_optional`, marker `tag_g_b`, attributes `g_b_attr_1` through `g_b_attr_6`, types `g_b_type_1` through `g_b_type_3`, roles `g_b_role_1` through `g_b_role_4`, booleans `g_b_bool_1` and `g_b_bool_2`, alias `g_b_alias_1`, and optional blocks tagged `tag_o1_b` through `tag_o7_b`.

## Control Flow
Global base rules are active immediately. Optional base blocks are enabled only after requirements are satisfied, often by module declarations from `module1.conf` or `module2.conf`; one block requiring `invalid_type` is intended to remain disabled.

## State And Persistence Behavior
The policydb contains base symbol tables, base allow rules including wildcard and complement permission sets, alias state, conditional rules, users, contexts, and optional declaration metadata. Linking modules can retroactively enable some optional declarations.

## Dependencies And Integration Points
It integrates with both linker modules and common test helpers for role type sets, attribute types, alias datums, and policydb index validation.

## Risks And Edge Cases
This fixture is sensitive to optional dependency iteration and cross-declaration visibility. Alias-driven optional `tag_o7_b` depends on module alias visibility, which is easy to mishandle.

## Test Signals
Expected signals are correct enabled tags, disabled invalid optional tags, merged type-attribute maps, role type-set additions, aliases `g_b_alias_1` and optionally `g_b_alias_2`, and valid indexes after linking.
