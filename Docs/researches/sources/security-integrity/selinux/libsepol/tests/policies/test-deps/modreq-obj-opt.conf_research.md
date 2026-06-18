# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-obj-opt.conf

## Purpose
This fixture tests optional object-class requirements and optional allow-rule activation.

## Important APIs, Types, And Functions
The global scope requires `class file { read }`, declares `mod_global_t`, `mod_foo_t`, and `mod_bar_t`. The optional block requires `class sem { create destroy }`, declares marker `mod_opt_t`, and grants `sem` permissions.

## Control Flow
The module links against both bases. If `sem` and its permissions exist, the optional block is enabled; otherwise the optional block is disabled without making the whole link fail.

## State And Persistence Behavior
The policydb should retain global module types regardless of optional state. The optional declaration’s allow rule is active only when enabled.

## Dependencies And Integration Points
It integrates class/permission require checking with optional declaration state and access-vector rule linking.

## Risks And Edge Cases
The module name is `modreq_obj_global` despite being the optional-object fixture, which can confuse report readers or test failure triage. The dependency signal still comes from `mod_opt_t`.

## Test Signals
Both links should return `0`, and `mod_opt_t` should be enabled only against the positive base.
