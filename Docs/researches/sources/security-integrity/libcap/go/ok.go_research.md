## sources/security-integrity/libcap/go/ok.go

Purpose: trivial executable used as a successful target for launcher and chroot tests.

Important APIs/functions: `main()` calls `os.Exit(0)`.

Control flow: immediate zero exit.

State/persistence: no state.

Dependencies/integration: built by `go/Makefile` with `CGO_ENABLED=0`; used by `try-launching` as a chroot-friendly binary.

Risks: must remain simple/static enough for chroot tests; adding imports or dynamic dependencies would weaken its role.

Test signals: `make -C go ok` and `try-launching` cases that execute `/ok` inside a chroot.
