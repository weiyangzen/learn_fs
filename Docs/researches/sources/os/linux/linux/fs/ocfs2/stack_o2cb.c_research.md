# File Research: sources/os/linux/linux/fs/ocfs2/stack_o2cb.c

`stack_o2cb.c` implements the OCFS2 stack plugin for the classic in-kernel o2cb cluster stack. It adapts OCFS2 stackglue operations to o2dlm, o2net, heartbeat, and nodemanager APIs.

Main responsibilities:
- Verifies at compile time that stackglue DLM lock mode constants match o2dlm `LKM_*` constants.
- Maps generic DLM lock flags to o2dlm flags in `flags_to_o2dlm()`.
- Maps o2dlm status codes to Linux errno values in `status_map` / `dlm_status_to_errno()`, preserving special meanings expected by OCFS2 dlmglue:
  - success as `0`
  - trylock failure as `-EAGAIN`
  - cancel-after-grant as `-EBUSY`
  - successful cancel as `-DLM_ECANCEL`
- Wraps o2dlm AST callbacks:
  - `o2dlm_lock_ast_wrapper()` dispatches grant ASTs to the active cluster protocol.
  - `o2dlm_blocking_ast_wrapper()` dispatches blocking ASTs.
  - `o2dlm_unlock_ast_wrapper()` maps status to errno and suppresses duplicate cancel-after-grant completion.
- Implements DLM operations:
  - `o2cb_dlm_lock()` calls `dlmlock()`.
  - `o2cb_dlm_unlock()` calls `dlmunlock()`.
  - `o2cb_dlm_lock_status()` reads status from the o2dlm lock status block.
  - `o2cb_dlm_lvb_valid()` always returns true because o2dlm zeroes lost LVB state rather than marking it invalid.
  - `o2cb_dlm_lvb()` returns the o2dlm LVB pointer.
  - `o2cb_dump_lksb()` dumps a lock by o2dlm lock id.
- Checks cluster readiness in `o2cb_cluster_check()`:
  - verifies this node is configured.
  - verifies heartbeat is active for this node.
  - compares heartbeat node map and o2net connected node map for up to 60 seconds.
  - reports nodes that are heartbeating but not reachable over o2net.
- Implements cluster connection lifecycle:
  - `o2cb_cluster_connect()` runs the cluster check, allocates private state, registers an eviction callback, computes the DLM domain key from CRC32 of the lockspace name, registers the DLM domain, stores negotiated protocol version, and registers eviction handling.
  - `o2cb_cluster_disconnect()` unregisters eviction callback and DLM domain, then frees private state.
  - `o2cb_cluster_this_node()` returns the configured local node number with range checks.
- Registers the plugin:
  - `o2cb_stack_ops` provides stackglue callbacks.
  - `o2cb_stack` is named `"o2cb"`.
  - module init/exit register and unregister with `ocfs2_stack_glue`.

Key invariants:
- OCFS2 does not join an o2cb lockspace until heartbeat and o2net connectivity agree for all heartbeating nodes.
- o2dlm eviction callbacks drive OCFS2 recovery callbacks for dead nodes.
- The DLM domain key must be stable across all nodes mounting the same domain, so it is derived from the shared connection name.
