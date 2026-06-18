# sources/security-integrity/libcap/tests/noop.c

Purpose: static no-op executable for launcher and chroot tests.

Important APIs/functions: `main()` immediately exits 0.

Control flow/state/dependencies: no state and no dependencies beyond libc. Built statically by the tests Makefile so it can run inside a chroot without shared libraries.

Integration points: `libcap_launch_test.c` launches `/noop` after `cap_launcher_set_chroot(".")`.

Risks and test signals: intentionally minimal; failure means execution environment or static linking is broken rather than application logic.
