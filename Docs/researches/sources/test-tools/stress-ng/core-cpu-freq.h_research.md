# sources/test-tools/stress-ng/core-cpu-freq.h

Purpose: declares `stress_cpu_freq_get`.

Important APIs and control flow: caller supplies output pointers for average, min, and max GHz.

State and persistence: no header state.

Dependencies and integration: used by metrics/buildinfo paths that report CPU frequency.

Risks and test signals: callers must pass valid pointers. Signal is successful linkage with platform implementation.
