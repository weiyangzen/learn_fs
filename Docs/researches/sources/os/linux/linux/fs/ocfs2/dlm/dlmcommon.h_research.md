# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmcommon.h

## Purpose
Internal common header for the OCFS2 DLM. It defines core DLM data structures, message IDs and wire formats, lock/resource state flags, helper functions, and cross-file function declarations.

## Core Constants
- Heartbeat callback priorities for DLM node up/down.
- `DLM_LOCKID_NAME_MAX` of 32 bytes.
- unknown owner marker `DLM_LOCK_RES_OWNER_UNKNOWN`.
- hash sizing constants for lock resources and master-list entries.
- recovery lock name `$RECOVERY`.

## Master List Entries
`struct dlm_master_list_entry` tracks lock-resource mastership discovery/migration:
- hash/list linkage
- DLM context
- spinlock, waitqueue, refs
- maybe/vote/response/node maps
- master/new master
- MLE type
- heartbeat callbacks
- associated lock resource/name/hash.

## DLM Context
`struct dlm_ctxt` is the domain-level state object. It includes:
- lock resource hash
- dirty/purge/pending AST/BAST/tracking lists
- domain node maps
- recovery context
- master hash and MLE heartbeat events
- counters
- debugfs root
- refs/domain state/join count
- heartbeat callbacks
- DLM and recovery threads
- worker queue and work list
- domain message handlers and eviction callbacks
- filesystem and DLM protocol versions.

## Lock Resource
`struct dlm_lock_resource` represents one named lock resource:
- hash node and qstr name
- kref
- granted/converting/blocked lock lists
- purge/dirty/recovering/tracking lists
- last-used timestamp
- owner node
- state flags
- LVB
- inflight lock/assert-worker counters
- AST reservations
- refmap.

State flags include uninitialized, recovering, ready, dirty, in-progress, migrating, dropping-ref, block-dirty, setref-in-progress, and recovery-waiting.

## Lock
`struct dlm_lock` wraps `struct dlm_migratable_lock` plus:
- list links for resource and AST/BAST queues
- lock resource pointer
- spinlock and kref
- AST/BAST callbacks and data
- lockstatus pointer
- pending flags for AST, BAST, convert, lock, cancel, unlock
- kernel-allocated LKSB flag.

## Wire Message IDs
Defines DLM message IDs beginning at 500:
- master request/assert/requery
- create/convert/unlock lock
- proxy AST
- deref lockres and done
- migration request/migratable lockres
- join/cancel/exit domain
- recovery begin/finalize/data done
- query region/nodeinfo.

These IDs are sent over the O2CB TCP message transport.

## Wire Structures
Defines network packet layouts for:
- master requests and assertions
- migrate requests and migratable lock resources
- create/convert/unlock lock messages
- proxy AST messages
- join/query/cancel domain messages
- recovery messages
- deref lockres messages
- region/nodeinfo query responses.

The migratable lock-resource layout is designed to fit up to 240 locks in one O2NET payload, leaving reserved bytes for future use.

## Helper Functions
Inline helpers cover:
- list index to text/list pointer
- empty LVB check
- lock-resource state to DLM status
- lock-cookie node/sequence decoding
- recovery lock name test
- lock mode printable name
- NL/PR/EX compatibility
- lock membership on a list
- errno-to-DLM-status conversion
- bitmap node iteration
- setting/changing lock-resource owner.

## Function Declaration Surface
Declares internal functions for:
- lock allocation/refcounting/attachment
- network message handlers
- pending convert/lock rollback and cancel/unlock commit
- DLM and recovery thread lifecycle
- recovery waits and node death checks
- DLM context refs and domain state
- lock-resource hash lookup/insert/remove
- lock-resource refmaps and inflight refs
- AST/BAST queueing and proxy sends
- dirtying/kicking lock resources
- heartbeat callbacks
- migration/recovery/mastership handlers
- purge and dealloc helpers
- slab cache lifecycle.

## Architectural Role
This header is the central contract between DLM implementation files. It binds together the domain state machine, lock-resource lifecycle, distributed mastership protocol, recovery protocol, and O2NET wire protocol.
