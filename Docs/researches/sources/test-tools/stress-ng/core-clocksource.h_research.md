# sources/test-tools/stress-ng/core-clocksource.h

Purpose: declares the clocksource performance check.

Important APIs and control flow: exposes `stress_clocksource_check`.

State and persistence: no header state.

Dependencies and integration: included by runtime code that wants to warn about HPET.

Risks and test signals: minimal; signal is successful linkage with `core-clocksource.c`.
