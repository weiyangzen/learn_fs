# sources/object-store/minio-mc/cmd/admin-kms-key-create.go

## Purpose
Implements `mc admin kms key create`, creating a new KMS master key by name.

## Important APIs, types, and functions
`adminKMSCreateKeyCmd` declares the command. `mainAdminKMSCreateKey` validates exactly two arguments, calls `newAdminClient`, invokes `CreateKey`, and conditionally prints terminal success.

## Control flow
The handler rejects invalid arity, creates an admin connection for the target, extracts the key ID, sends the create request, and prints a green success line only when stdout is a terminal.

## State and persistence behavior
The persistent mutation is remote KMS key creation through the MinIO admin API. No local state is stored, and non-terminal output is intentionally silent on success.

## Dependencies and integration points
It integrates KMS admin APIs, `probe` errors, terminal detection through `golang.org/x/term`, `os.Stdout`, and console/color output.

## Risks and edge cases
Quiet success for non-terminal stdout may surprise automation that expects a message. Key name validation is delegated to the server/KMS backend. Create is not idempotently handled locally.

## Test signals
Tests should cover arity checks, successful `CreateKey` invocation, server error propagation, terminal versus non-terminal success output, and names containing unusual but server-accepted characters.
