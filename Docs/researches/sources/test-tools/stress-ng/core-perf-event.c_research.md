# sources/test-tools/stress-ng/core-perf-event.c

Purpose: small compile unit that includes Linux perf event definitions when available.

Important APIs/types: does not define runtime APIs; conditionally includes `<linux/perf_event.h>` after `config.h`.

Control flow: none beyond preprocessor gating.

State/persistence: no state.

Dependencies/integration: participates in build/config checks around `HAVE_LINUX_PERF_EVENT_H` and supports perf-related compilation.

Risks: its value is build-system oriented; missing or incompatible kernel headers should be caught at compile time.

Test signals: build on Linux with perf headers and on systems without them.
