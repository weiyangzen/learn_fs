# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-obj-global.conf

## Purpose
This module validates global object-class dependency checking.

## Important APIs, Types, And Functions
It requires `class sem { create destroy }`, declares marker `mod_global_t`, creates `mod_foo_t` and `mod_bar_t`, and grants `sem` permissions between them.

## Control Flow
`do_deps_modreq_global()` links this module into the positive and negative bases. The positive path must merge the module and enable the marker declaration; the negative path must fail due to missing class or permission requirements.

## State And Persistence Behavior
Successful linking adds module-local types and an access-vector rule for the `sem` object class. Failed linking should not partially enable module declarations.

## Dependencies And Integration Points
The fixture targets the class/permission half of require resolution, not type or role resolution. It is sensitive to base object-class definitions.

## Risks And Edge Cases
Only one class and two permissions are tested. A base that declares `sem` but not both permissions should still be treated as unmet, so preserving exact class permission sets matters.

## Test Signals
Expected signals are success with the met base and `-3` with the unmet base, plus an enabled `mod_global_t` declaration on success.
