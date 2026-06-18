# sources/test-tools/stress-ng/core-processes.h

Purpose: declares the process diagnostic dump helper.

Important APIs/types: `stress_processes_dump(void)`.

Control flow: no header flow.

State/persistence: no state; implementation only logs diagnostics.

Dependencies/integration: included by code paths that want a process snapshot, especially failure or status reporting.

Risks: callers should treat it as best-effort and platform-dependent.

Test signals: compile all callers and exercise diagnostic output on Linux and no-op behavior elsewhere.
