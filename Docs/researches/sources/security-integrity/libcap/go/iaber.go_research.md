## sources/security-integrity/libcap/go/iaber.go

Purpose: helper/regression program that sets an IAB tuple, execs itself, and validates capability inheritance behavior across exec.

Important APIs/functions: `cap.SetUID`, `cap.GetProc`, `cap.IABGetProc`, `cap.IABFromText`, `IAB.SetProc`, and `syscall.Exec`.

Control flow: with no extra args logs success; otherwise changes UID to 1 if needed, logs current cap/IAB state, parses the first argument as IAB text, applies it to the process, logs pre-exec state, and execs itself with remaining arguments.

State/persistence: mutates UID and IAB vectors of the current process; no files.

Dependencies/integration: Go cap package, Linux IAB/ambient/bounding semantics, exec behavior. Used by `go/Makefile` `sudotest`.

Risks: requires privilege for UID/IAB changes; failure leaves only logs; argument contract is terse.

Test signals: `sudo ./iaber` cases in `go/Makefile` that should pass/fail based on bounding drops and ambient/inheritable settings.
