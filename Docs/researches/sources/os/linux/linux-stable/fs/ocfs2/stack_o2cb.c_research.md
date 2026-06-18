# File Research: sources/os/linux/linux-stable/fs/ocfs2/stack_o2cb.c

Purpose: implements the OCFS2 stack glue plugin for the classic in-kernel o2cb cluster stack and o2dlm lock manager.

Read coverage: complete file read, 439 lines.

Key responsibilities:
- Maps generic OCFS2 stack lock modes and flags to o2dlm `LKM_*` values.
- Maps o2dlm status codes to Linux errno values used by OCFS2 dlmglue.
- Wraps o2dlm lock, blocking, and unlock AST callbacks into OCFS2 stack protocol callbacks.
- Provides cluster readiness checks before joining a lockspace.
- Registers/unregisters the o2cb stack plugin with OCFS2 stack glue.

Major logic:
- Compile-time checks ensure OCFS2/DLM lock mode values match o2dlm modes.
- `flags_to_o2dlm()` translates generic stack flags including noqueue, cancel, convert, LVB, orphan, force unlock, timeout, and local.
- `dlm_status_to_errno()` maps the o2dlm status enum to errno; special mappings for normal, not queued, cancel grant, and successful cancel must remain unique for dlmglue semantics.
- `o2cb_dlm_lock()` and `o2cb_dlm_unlock()` call `dlmlock()` / `dlmunlock()` with wrapper callbacks and translate status codes.
- `o2cb_cluster_check()` verifies local node configuration, heartbeat participation, and o2net connectivity to all heartbeating nodes, waiting up to 60 seconds for maps to stabilize.
- `o2cb_cluster_connect()` allocates private eviction callback state, computes a DLM key from the domain name with CRC32, registers the DLM domain, negotiates protocol version, and registers eviction callback.
- `o2dlm_eviction_cb()` reports evicted nodes and calls OCFS2 recovery handler.
- `o2cb_cluster_disconnect()` unregisters eviction callback, unregisters the DLM domain, and frees private state.

Important entry points:
- Stack operations: `o2cb_cluster_connect()`, `o2cb_cluster_disconnect()`, `o2cb_cluster_this_node()`, `o2cb_dlm_lock()`, `o2cb_dlm_unlock()`.
- LVB/status helpers: `o2cb_dlm_lock_status()`, `o2cb_dlm_lvb_valid()`, `o2cb_dlm_lvb()`, `o2cb_dump_lksb()`.
- Module lifecycle: `o2cb_stack_init()`, `o2cb_stack_exit()`.

Concurrency and dependencies:
- Depends on o2nm node manager, o2hb heartbeat, o2net connectivity, o2dlm domain/lock APIs, and OCFS2 stackglue.
- Eviction callbacks bridge o2dlm membership changes into OCFS2 recovery handling.
- LVB validity is always reported true because o2dlm zeroes lost LVB content rather than exposing invalid content.

Risks and edge cases:
- `o2cb_cluster_check()` is intentionally racy but improves diagnostics before `dlm_register_domain()` fails cryptically.
- `DLM_CANCELGRANT` is ignored in unlock AST because the lock grant AST is expected to handle the granted lock.
- Incorrect status-map uniqueness would break higher-level dlmglue handling of trylock, cancel, and cancel-after-grant cases.
