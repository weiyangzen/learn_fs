# sources/security-integrity/fscrypt/pam/pam.go

## Purpose
`pam.go` wraps libpam handles and transactions for Go code and PAM modules, including PAM data storage, item access, privilege switching to the PAM user, messaging, transaction start/end, and authentication.

## Important APIs, Types, and Functions
`Handle` wraps `pam_handle_t` and tracks `status`, original privileges, and `PamUser`. Public methods include `NewHandle`, `ClearData`, `SetSecret`, `GetSecret`, `SetString`, `GetString`, `GetItem`, `GetServiceName`, `StartAsPamUser`, `StopAsPamUser`, and `InfoMessage`. `Transaction` supports `Start`, `End`, and `Authenticate`.

## Control Flow
`NewHandle` retrieves the PAM username and resolves it through `os/user`. Data helpers allocate C strings or locked secret copies and register cleanup callbacks. `StartAsPamUser` saves current process privileges and switches effective UID/GID/groups to the PAM user. `StopAsPamUser` restores saved privileges. `Start` calls `pam_start` with `goConv`, while `Authenticate` invokes `pam_authenticate` with disallow-null and optional silent flags.

## State and Persistence
State is stored in the live PAM handle and process credentials. Secrets stored with `SetSecret` are copied into locked C memory and later wiped by C cleanup. `origPrivs` in `Handle` tracks whether privilege restoration is needed.

## Dependencies and Integration Points
Uses cgo libpam, C helpers from `pam.h`, `security` privilege management, and `os/user`. `pam_fscrypt` depends heavily on `Handle` for authentication/session/password hooks.

## Risks
Process-wide privilege switching is sensitive in Go and must be balanced. PAM data pointers are raw C memory and type correctness is manual. `ClearData` replaces data with an empty C string rather than removing the key outright. Authentication false is separated from PAM execution errors.

## Test Signals
Local `pam_test.go` is a trivial compile/pass test. Real confidence comes from build integration and PAM module workflows, not unit coverage.
