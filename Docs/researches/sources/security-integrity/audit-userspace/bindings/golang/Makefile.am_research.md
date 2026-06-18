<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/golang/Makefile.am

Purpose: automake packaging/install rules for Go libaudit bindings.

Important build API: distributes `audit.go`, marks `test.go` as a dist check script, and under `HAVE_GOLANG` installs `audit.go` under `$(prefix)/lib/golang/src/pkg/redhat.com/audit`. The `check` target stages files but leaves actual `go run` disabled due to Go path limitations.

Control flow and state: install/uninstall are hand-written shell recipes. Check creates and removes a temporary `audit` directory.

Dependencies and integration: depends on top source `bindings/golang/audit.go` and `lib/libaudit.h`; runtime cgo uses `pkg-config: audit`.

Risks and test signals: test coverage is effectively disabled, so build/package regressions can slip through. The old GOPATH-style install path may be incompatible with modern Go module workflows.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/golang/Makefile.am -->
