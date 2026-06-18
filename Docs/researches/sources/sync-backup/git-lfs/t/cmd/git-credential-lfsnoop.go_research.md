# sources/sync-backup/git-lfs/t/cmd/git-credential-lfsnoop.go

Purpose: placeholder credential helper binary built for test tooling.

Important API: empty `main`.

Control flow: exits successfully without reading input or producing output.

State/persistence behavior: no state and no persistence.

Dependencies/integration: included in `t/Makefile` helper builds under the `testtools` build tag, likely used where the presence of a credential helper executable matters.

Risks: any test expecting behavior from this helper would fail silently because it intentionally does nothing.

Test signals: build success and zero exit status.
