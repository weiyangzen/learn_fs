# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/module.conf

## Purpose
This general module fixture combines ordinary module requires, a new domain type, role type assignment, unconditional allow rules, and a conditional allow rule.

## Important APIs, Types, And Functions
It requires `secure_mode`, `system_t`, `sysadm_t`, `file_t`, attribute `domain`, role `system_r`, and `class file { read write }`. It declares `new_t, domain`, assigns `system_r types new_t`, grants `system_t file_t:file`, and conditionally grants `sysadm_t file_t:file` under `secure_mode`.

## Control Flow
The module is parsed as a standalone policy module and can be linked with the dependency base. The unconditional allow should always be present after link; the conditional allow becomes a conditional node tied to a base boolean.

## State And Persistence Behavior
Linking adds a new type, attribute membership, role type-set membership, access-vector rules, and a conditional expression to the target base policydb.

## Dependencies And Integration Points
This file integrates type, attribute, role, class, permission, and boolean require resolution in one compact module.

## Risks And Edge Cases
It is broader but less isolated than the `modreq-*` fixtures, so a failure can come from several symbol families. It assumes `secure_mode` exists in the base even though its default value is false.

## Test Signals
Useful signals are successful parsing/linking, active `new_t` role membership, and creation of the conditional rule for `secure_mode`.
