# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/base-base-only.conf

## Purpose
This is a minimal base-only expander fixture used to validate expansion without any module overlay.

## Important APIs, Types, And Functions
It declares `security` and `file` classes, `sid kernel`, common file permissions, optional MLS data under `enable_mls`, attribute `myattr`, type `mytype_t`, role `myrole_r`, boolean `mybool`, user `myuser_u`, and a kernel SID context.

## Control Flow
The file is loaded as a base policy and expanded directly. There are no module dependency or optional interactions beyond the MLS macro guard.

## State And Persistence Behavior
The fixture seeds the smallest useful policydb state: classes, one SID, MLS state when enabled, a type/role/user relationship, and an initial SID context.

## Dependencies And Integration Points
It integrates with the expander’s base-only path and parser macros `gen_user` and `gen_context`.

## Risks And Edge Cases
Because it is intentionally tiny, adding module-like constructs would weaken its value as a base-only control. With MLS disabled, `gen_user` ranges must still parse consistently.

## Test Signals
Successful load and expansion verify that base policy expansion does not require modules or the larger reference scaffolding.
