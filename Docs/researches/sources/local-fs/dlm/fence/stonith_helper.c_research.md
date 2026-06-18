# File Research: sources/local-fs/dlm/fence/stonith_helper.c

## Purpose
Small helper that asks Pacemaker/STONITH to fence a failed DLM node.

## Behavior
- Accepts `-n <nodeid>` and `-t <fail_time>` from argv, or reads `node=<id>` and `fail_time=<time>` key/value pairs from stdin.
- Requires a nonzero node id.
- If `fail_time` is supplied, calls `stonith_api_time_helper(nodeid, 0)` and exits successfully if the node has already been fenced at or after that time.
- Otherwise calls `stonith_api_kick_helper(nodeid, 300, 0)` with a 300-second timeout.
- Logs fencing failures to stderr and syslog under `dlm_stonith`.

## Dependencies
- Pacemaker `crm/stonith-ng.h`.

## Risks / Gaps
- Minimal validation on input values.
- Global `nodeid` and `fail_time` are simple process-wide state; fine for this one-shot helper.
