<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success.c -->
## sources/test-tools/strace/tests/arch_prctl-success.c

Purpose: Wrapper that forces `arch_prctl.c` through injected successful-return paths.

Important APIs/types/functions: Defines `INJECT_RETVAL` and includes `arch_prctl.c`.

Control flow: The included main parses `NUM_SKIP INJECT_RETVAL`, waits until a marker `arch_prctl(-1, -2)` call returns the injected value, then runs the full command/xfeature matrix with success annotations.

State and persistence: Uses included temporary buffers; may perform real `ARCH_SET_*` attempts under injection control.

Dependencies and integration: Used by success and xlat-success executables and by `arch_prctl.sh` through strace injection arguments.

Risks: If injection setup does not lock onto the marker call, the test fails early. Host arch support still controls syscall availability.

Test signals: Expected output contains injected return text and successful pointer dereference formatting for commands normally failing.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success.c -->
