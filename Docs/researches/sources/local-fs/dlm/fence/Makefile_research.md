# File Research: sources/local-fs/dlm/fence/Makefile

## Purpose
Builds and installs `dlm_stonith`, a Pacemaker-backed fencing helper.

## Build Behavior
- Compiles `stonith_helper.c`.
- Uses hardening flags similar to other DLM user tools.
- Uses `pkg-config --cflags pacemaker-fencing` and errors out if Pacemaker fencing headers are unavailable.
- Links with `-ldl`.
- Installs binary to `$(PREFIX)/sbin` and `dlm_stonith.8` to man8.

## Notes
- The link line relies on Pacemaker fencing symbols being provided through included build/link environment or dynamic loading semantics; the Makefile only explicitly adds `-ldl`.
