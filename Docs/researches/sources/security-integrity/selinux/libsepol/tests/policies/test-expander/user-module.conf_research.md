# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/user-module.conf

## Purpose
This module is a minimal user-require fixture for expander tests.

## Important APIs, Types, And Functions
It requires `class file { read write }` and, under `enable_mls`, `user user_check_1`.

## Control Flow
In MLS-enabled parsing, the module depends on the user declared by `user-base.conf`. In non-MLS parsing, the user require is omitted by the macro guard.

## State And Persistence Behavior
The module does not add active rules or symbols beyond requirements; its value is in whether user scope checking succeeds during link.

## Dependencies And Integration Points
It integrates with user symbol tables, m4 MLS guards, and the expander’s module link path.

## Risks And Edge Cases
Because the module has no marker type or rule body, failures are mostly load/link failures. It is easy to underestimate because its behavior changes with MLS configuration.

## Test Signals
Expected signals are successful parsing and link when `user_check_1` is available in MLS mode.
