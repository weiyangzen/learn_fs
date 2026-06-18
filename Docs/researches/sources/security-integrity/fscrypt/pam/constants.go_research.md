# sources/security-integrity/fscrypt/pam/constants.go

## Purpose
`pam/constants.go` exposes selected Linux PAM item and flag constants to Go code via cgo.

## Important APIs, Types, and Functions
`Item` wraps PAM item identifiers such as `Service`, `User`, `Tty`, `Rhost`, `Authtok`, `Oldauthtok`, `Ruser`, and `UserPrompt`. `Flag` wraps PAM flags such as `Silent`, `DisallowNullAuthtok`, credential flags, `ChangeExpiredAuthtok`, `PrelimCheck`, and `UpdateAuthtok`.

## Control Flow
There is no runtime logic; constants are assigned from C PAM macros at compile time.

## State and Persistence
No state or persistence. These constants parameterize PAM calls in `pam.go` and `pam_fscrypt.go`.

## Dependencies and Integration Points
Uses cgo and links `-lpam`, including `<security/pam_modules.h>`. Values are consumed by handle item access, authentication, and password-change hooks.

## Risks
Requires PAM development headers and libpam at build time. Constant availability follows the target platform PAM implementation.

## Test Signals
Only indirect coverage through PAM wrapper and module code; `pam_test.go` is a stub.
