# sources/security-integrity/selinux/libsepol/tests/policies/test-linker/module2.conf

## Purpose
This second linker module completes the cross-module merge matrix by consuming symbols declared by `module1.conf` and contributing more role, attribute, type, boolean, and optional state.

## Important APIs, Types, And Functions
It requires `g_b_attr_5`, `g_b_attr_6`, `g_m1_attr_3`, and `o3_m1_attr_2`, declares marker `tag_g_m2`, types `g_m2_type_*`, role `g_m2_role_1`, additions to base roles, booleans `g_m2_bool_1` and `g_m2_bool_2`, and optional tags `tag_o1_m2` and `tag_o2_m2`.

## Control Flow
The global block links after `module1.conf` provides its required module attribute. Optional block `o1` depends on `optional_type`; optional block `o2` depends on `g_m1_attr_4` and `o4_m1_attr_1`.

## State And Persistence Behavior
Successful linking adds cross-module attribute memberships, role type-set additions, and a conditional rule controlled by two module booleans. It also validates that module2 can add types to attributes originating in base optionals and module1 optionals.

## Dependencies And Integration Points
It integrates tightly with `module1.conf` and `small-base.conf`, stressing multi-module link ordering and optional dependency resolution.

## Risks And Edge Cases
If modules are linked in isolation or in the wrong dependency visibility phase, required module attributes can appear missing. Conditional mapping also depends on both module booleans being represented consistently.

## Test Signals
Expected signals are successful link with module1, correct activation of satisfied optionals, and final type/role/attribute sets that include contributions from both modules.
