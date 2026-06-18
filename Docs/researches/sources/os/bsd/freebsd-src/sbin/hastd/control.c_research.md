# File Research: sources/os/bsd/freebsd-src/sbin/hastd/control.c

`control.c` implements HAST control-plane handling between `hastctl`, the parent daemon, and worker processes.

Key behavior:
- `child_cleanup()` closes worker control/event/connection proto channels and clears the worker pid.
- Role changes:
  - Resolve resource by name.
  - Return previous role in the response.
  - If role changes, log it, update resource role, kill/wait for an existing worker, and start a primary worker when entering primary role.
  - Execute configured hooks for role transitions.
- `control_handle()` accepts a control socket connection from `hastctl`, receives an nv command, validates fields, dispatches `setrole` or `status`, and sends an nv response.
- Supports operating on all resources or selected resource names.
- `control_status()` emits static resource status fields and, when a worker exists, asks the worker for live status.
- `control_status_worker()` sends a `CONTROL_STATUS` request over the parent-worker control channel and copies worker counters/queue sizes into the user response.
- `ctrl_thread()` runs in a worker and handles parent requests:
  - `CONTROL_STATUS` returns complete/degraded status, dirty bytes, extent/keepdirty settings, I/O counters, error counters, and role-specific auxiliary queue information.
  - `CONTROL_RELOAD` applies primary config reload state.
  - Unknown commands return `EINVAL`.

Important details:
- Primary role asserts a worker should exist for status.
- Secondary status can be reported with or without a worker depending on state.
- Worker status treats missing remote input/output connections as degraded.
