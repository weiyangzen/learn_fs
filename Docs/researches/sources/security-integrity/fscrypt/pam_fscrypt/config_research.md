# sources/security-integrity/fscrypt/pam_fscrypt/config

## Purpose
This file is the PAM profile metadata for installing/enabling `pam_fscrypt` passphrase support.

## Important APIs, Types, and Functions
It declares the profile name, default enablement, priority, and auth/session/password stack entries using `PAM_INSTALL_PATH`.

## Control Flow
There is no program control flow. The PAM stack consumes these directives during installation or configuration.

## State and Persistence
When installed, it influences persistent PAM configuration by adding optional auth, session, and password hooks for the fscrypt PAM module.

## Dependencies and Integration Points
Integrates with PAM configuration tooling and the built shared object path substituted for `PAM_INSTALL_PATH`. It corresponds to exported functions in `pam_fscrypt.go`.

## Risks
Because hooks are optional, module failures may not block login depending on PAM stack behavior, but password/session integration can still affect unlock/lock behavior. Incorrect install path substitution would make the profile ineffective.

## Test Signals
No automated tests for this config file in the subset. Behavior is validated by packaging or PAM integration tests.
