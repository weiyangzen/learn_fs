# File Research: sources/local-fs/dlm/dlm_controld/helper.c

## Purpose
Child helper process for running a restricted set of distributed commands requested through daemon CPG run messages, then reporting results back to the main daemon.

## Main Behavior
- Maintains up to 32 running commands, mapping pid to run UUID and command id.
- `_get_cmd_id()` allowlists only:
  - `lvm lvchange --refresh ...`
  - `lvm lvs ...`
- `exec_command()` tokenizes a command string with limited backslash escaping, reports the recognized command id to its helper parent through a pipe, then `execvp()`s only if allowed.
- `run_helper()`:
  - Clears supplementary groups.
  - Sends periodic blank status replies to the main daemon.
  - Polls an input fd for `run_request` messages.
  - Forks a child for each request and records its pid/uuid/cmd id.
  - Handles `DLM_MSG_RUN_CANCEL` by clearing tracking state for the UUID.
  - Uses `waitid(P_ALL, WEXITED | WNOHANG)` to collect child exits.
  - Sends `run_reply` messages containing UUID, pid, and local result.
  - Logs nonzero results to syslog.

## Integration Points
- Parent/main daemon side is in `main.c` and `daemon_cpg.c` through `send_helper_run_request()`, `receive_run_request()`, and `receive_run_reply()`.
- Uses `RUN_UUID_LEN`, `RUN_COMMAND_LEN`, `run_request`, and `run_reply` from `dlm_daemon.h`.

## Risks and Notes
- Command parsing is restrictive and avoids shell execution; this is important because commands arrive through cluster messages.
- Cancel currently does not kill the running child; it only removes bookkeeping.
- Duplicated argument strings are not freed in the child before exec/exit, which is not significant for one-shot child processes.
- If helper bookkeeping loses a pid, the exit is logged and no UUID result is sent.
