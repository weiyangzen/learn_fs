# sources/object-store/minio-mc/cmd/admin-inspect.go

## Purpose
Maintains the deprecated hidden `mc admin inspect` command and redirects users to `mc support inspect`.

## Important APIs, types, and functions
`adminInspectCmd` defines the hidden command. `mainAdminInspect` calls `deprecatedError("mc support inspect")`.

## Control flow
The command does not perform inspection. All invocations route directly to the shared deprecation error.

## State and persistence behavior
No server or local state is accessed. The old admin inspection path is disabled in favor of the support command.

## Dependencies and integration points
It depends on `minio/cli`, global initialization, and deprecation plumbing. It remains registered under top-level admin for compatibility.

## Risks and edge cases
Because the command is hidden but still registered, stale documentation or scripts may still hit it. Replacement guidance must remain accurate.

## Test signals
Tests should verify hidden registration and that invocation returns the `mc support inspect` deprecation message without attempting admin API calls.
