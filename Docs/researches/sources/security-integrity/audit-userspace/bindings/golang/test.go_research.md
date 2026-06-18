<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/test.go -->
# sources/security-integrity/audit-userspace/bindings/golang/test.go

Purpose: minimal executable test for the Go audit binding's encoding predicate.

Important APIs and functions: imports local `./audit`, calls `AuditValueNeedsEncoding("test")` expecting false and `AuditValueNeedsEncoding("test test")` expecting true, prints failure messages or `Success`.

Control flow and state: exits by returning from `main` after printing on failure; no explicit nonzero exit is used.

Dependencies and integration: intended to run after staging `audit.go` into a local package, but the Makefile currently disables actual execution.

Risks and test signals: because failures do not call `os.Exit(1)` and the check is disabled, this is weak as automated coverage. It still documents expected encoding behavior for whitespace-containing values.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/test.go -->
