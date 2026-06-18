# File Research: sources/virtualization/nbd/tests/run/cwrap_test

## Purpose
Wrapper script for running `simple_test` under socket-wrapper/nss-wrapper.

## Behavior
Creates a temporary `SOCKET_WRAPPER_DIR`, sets `LD_PRELOAD` to `libsocket_wrapper.so libnss_wrapper.so`, installs a cleanup trap, runs sibling `simple_test` with the same arguments, and exits with the test status.

## Dependencies
Requires POSIX shell, `mktemp`, socket-wrapper, and nss-wrapper libraries.

## Risks and Notes
The script relies on dynamic loader `LD_PRELOAD` semantics and does not quote every expansion, matching test-harness assumptions.
