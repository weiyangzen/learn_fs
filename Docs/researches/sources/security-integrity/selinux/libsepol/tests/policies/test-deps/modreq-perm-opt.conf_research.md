# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-perm-opt.conf

## Purpose
This module tests permissions required inside an optional declaration.

## Important APIs, Types, And Functions
The module globally requires `class file { read write }` and declares `mod_global_t`. The optional block requires `class msg { send receive }`, declares marker `mod_opt_t`, creates `a_mod_t` and `b_mod_t`, and grants `msg` permissions.

## Control Flow
`deps_modreq_opt()` expects the positive base to link and enable the optional block. The negative permission case expects `link_modules()` to return `-3`, making it stricter than most optional fixtures.

## State And Persistence Behavior
When positive, the optional declaration contributes active types and an access-vector rule. When negative, the module is rejected by the linker rather than merely leaving `mod_opt_t` disabled.

## Dependencies And Integration Points
This fixture probes a nuanced linker path where optional permission requirements interact with class resolution and access-vector rule validation.

## Risks And Edge Cases
The asymmetric expectation, success for most missing optional symbols but failure for missing optional permissions, is a regression-prone contract. Changes to optional handling should revisit this fixture explicitly.

## Test Signals
Positive link return `0` with enabled `mod_opt_t`; negative link return `-3`.
