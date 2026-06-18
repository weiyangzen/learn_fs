# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmdomain.c

## Purpose
Defines OCFS2 DLM domain lifecycle: allocation, registration, join negotiation, leave/shutdown, network handler registration, heartbeat/node-region validation, and eviction callbacks.

## Main Entry Points
- `dlm_register_domain()` creates or references a DLM domain and joins the cluster domain.
- `dlm_unregister_domain()` leaves the domain, migrates locks, sends exit messages, and tears down workers/handlers.
- `dlm_lookup_lockres()` and internal lookup helpers locate lock resources in per-domain hashes.
- `dlm_grab()` / `dlm_put()` manage domain references.
- `dlm_domain_fully_joined()` checks whether network handlers may accept domain traffic.
- `dlm_fire_domain_eviction_callbacks()` runs filesystem eviction callbacks before recovery completes.

## Join Protocol
The file registers global join handlers for:
- `DLM_QUERY_JOIN_MSG`
- `DLM_ASSERT_JOINED_MSG`
- `DLM_CANCEL_JOIN_MSG`
- `DLM_QUERY_REGION`
- `DLM_QUERY_NODEINFO`

`dlm_try_to_join_domain()` snapshots live heartbeat nodes, asks each live node whether this node may join, gathers `JOIN_OK` responders into `domain_map`, validates node info and heartbeat regions for protocol 1.1+, sends join asserts, and transitions to `DLM_CTXT_JOINED`.

The protocol negotiates DLM and filesystem locking minor versions. Major mismatch or older remote minor than required fails with protocol mismatch. Join is rejected during recovery, parallel joins, stale domain-map visibility, or incompatible cluster configuration.

## Leave Protocol
`dlm_unregister_domain()` transitions to shutdown when the last join reference is dropped. It sends best-effort begin-exit messages for protocol 1.2+, kicks the DLM thread, repeatedly migrates or purges lock resources with `dlm_migrate_all_locks()`, marks the domain leaving after any active joiner clears, sends exit messages to remaining nodes, force-frees MLEs, and unregisters handlers/threads/workqueue.

## Context and Resource Management
`dlm_alloc_ctxt()` allocates hash page vectors for lock resources and MLEs, initializes all lists, locks, waitqueues, recovery state, counters, worker infrastructure, and debugfs subroot. `dlm_ctxt_release()` removes failed or shut-down domains from the global list and frees memory.

## Locking
The file documents global spinlock order:
`dlm_domain_lock`, `dlm_ctxt->spinlock`, `dlm_lock_resource->spinlock`, `dlm_ctxt->master_lock`, `dlm_ctxt->ast_lock`, `dlm_master_list_entry->spinlock`, `dlm_lock->spinlock`.

This ordering is central because join/leave handlers and lookup paths combine global domain state, per-domain maps, lock resources, and MLE structures.
