# sources/test-tools/stress-ng/core-smart.h

Purpose: declares the S.M.A.R.T. monitoring hooks used at run start and stop.

Important APIs/types/functions: `stress_smart_start(void)` captures initial disk attribute data when enabled. `stress_smart_stop(void)` captures final data, reports changes, and cleans up.

Control flow: no header logic. The intended lifecycle is start once before stressors and stop once after completion.

State and persistence: implementation keeps snapshots in static process memory between the two calls.

Dependencies/integration: included by main run orchestration around global option `--smart`.

Risks: callers should pair start/stop; calling stop without start is safe but only reports according to implementation state.

Test signals: compile with and without SCSI SG support and verify lifecycle is no-op/reporting as expected.
