# sources/security-integrity/selinux/libsepol/tests/policies/test-linker/module1.conf

## Purpose
This is the first large linker module fixture. It tests cross-module and base/module merging for attributes, roles, aliases, booleans, conditionals, and optional declarations.

## Important APIs, Types, And Functions
It requires base roles, classes, attributes, and type `g_b_type_3`. It declares marker `tag_g_m1`, attributes `g_m1_attr_*`, types `g_m1_type_*`, roles `g_m1_role_1`, base role additions, alias `g_m_alias_1`, boolean `g_m1_bool_1`, and optional blocks tagged `tag_o1_m1` through `tag_o4_m1`.

## Control Flow
Global declarations should always merge. Optional blocks depend on `optional_type`, base attributes, `enable_optional`, or attributes from other modules. Some optionals intentionally reference absent requirements to remain disabled.

## State And Persistence Behavior
Linking mutates the base with new module symbols, type-attribute memberships, role type-set additions, aliases, conditional rules, and enabled optional declarations. It also exposes symbols that can enable base optional blocks and `module2.conf` optionals.

## Dependencies And Integration Points
This fixture pairs with `test-linker/small-base.conf` and `module2.conf`. It is used to verify that the linker resolves dependencies across base, module, and optional declaration boundaries.

## Risks And Edge Cases
The fixture deliberately relies on declaration ordering and cross-module requirements. A change to optional activation timing can affect base optional blocks and second-module optional blocks simultaneously.

## Test Signals
Expected signals include enabled marker tags for satisfied optionals, disabled tags for unsatisfied ones, correct merged attribute memberships, role type additions, alias resolution, and conditional mapping.
