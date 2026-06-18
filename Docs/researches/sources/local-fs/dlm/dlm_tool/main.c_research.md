# File Research: sources/local-fs/dlm/dlm_tool/main.c

## Purpose
Implements `dlm_tool`, the main administrative CLI for DLM lockspaces, daemon status/config/debug dumps, plocks, fencing acknowledgements, run commands, and kernel debugfs lock inspection.

## Command Areas
- Direct libdlm operations: `join`, `leave`, `joinleave`.
- Daemon operations through `dlm_controld`: `ls`, `status`, `dump`, `dump_config`, `reload_config`, `set_config`, `plocks`, `log_plock`, `fence_ack`, `run*`.
- `dlm_sand` fallback for status/debug/config query dumps where supported.
- Debugfs operations: `lockdump`, `lockdebug`.

## Key Logic
- `decode_arguments()` parses command, options, optional lockspace name, run UUID, or command payload.
- `_daemon_connect()` first tries `dlm_controld` sockets, then `dlm_sand` sockets when the command supports both.
- `_dlms_dump()` speaks the `dlm_sand` query protocol using `dlm_sd_header`.
- `_dlmc_*()` wrappers use `libdlmcontrol` APIs.
- `do_lockdebug()` parses modern and older debugfs formats, printing resources, locks, LVBs, toss entries, waiters, and optional summaries.
- `do_join()` and `do_leave()` call `dlm_new_lockspace()` / `dlm_release_lockspace()`.

## Dependencies
- `libdlm.h` for kernel lockspace creation/removal.
- `libdlmcontrol.h` and `dlm_controld.h` for daemon-control APIs.
- `dlm_sand_sock.h` for fallback query/control socket constants and headers.
- Kernel debugfs files under `/sys/kernel/debug/dlm`.

## Risks / Gaps
- Fixed `MAX_NODES` is 128 for `dlm_controld` node display, smaller than `dlm_sand`’s 2000-node model.
- `run_command` is built by repeated `strcat()` after length checks; acceptable but brittle.
- Some debugfs parsers are tightly coupled to text formats and fail noisily if kernel output changes.
- `daemon_reload_config()` and `daemon_set_config()` do nothing for `dlm_sand`; only query dumps are supported by this CLI path.
