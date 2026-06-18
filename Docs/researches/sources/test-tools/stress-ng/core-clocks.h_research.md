# sources/test-tools/stress-ng/core-clocks.h

Purpose: clock identifier compatibility header.

Important APIs and control flow: includes `<time.h>` and defines Linux `CLOCK_AUX` as 16 when absent.

State and persistence: compile-time only.

Dependencies and integration: used by clock-related stressors/helpers that need `CLOCK_AUX` even on older headers.

Risks and test signals: hard-coded clock IDs can diverge on unusual platforms. Signal is compilation and runtime handling of unsupported clocks.
