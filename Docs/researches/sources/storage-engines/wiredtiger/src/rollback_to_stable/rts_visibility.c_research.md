# sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_visibility.c

Purpose: centralizes RTS visibility predicates used to decide whether update chains, transactions, and pages contain unstable content that must be rolled back.

Important APIs and functions: `__wti_rts_visibility_has_stable_update` detects a surviving non-aborted update in a processed chain. `__wti_rts_visibility_txn_visible_id` evaluates transaction-id visibility against the recovered checkpoint snapshot during recovery. `__wti_rts_visibility_page_needs_abort` inspects page/ref reconciliation metadata and returns whether a page must be read and processed. The static `__rts_visibility_get_ref_max_durable_timestamp` applies history-store-specific aggregate timestamp rules.

Control flow: transaction visibility is trivial outside recovery, true when no checkpoint snapshot exists, and otherwise delegates to snapshot-id visibility. Page visibility first treats in-memory btrees as needing rollback. It then checks reconciled replace and multiblock page-modify results, instantiated deleted-page metadata, on-page address cells, or off-page addresses. For each source it computes the relevant maximum durable timestamp, prepared flag, newest transaction id, and returns true if the durable timestamp exceeds rollback, prepared updates exist, or recovery transaction checks demand rollback.

State and persistence behavior: this file is read-only except for verbose logging. It reads `WT_REF`, `WT_PAGE_MODIFY`, `WT_ADDR`, `WT_TIME_AGGREGATE`, `WT_PAGE_DELETED`, btree flags, and connection recovery snapshot state.

Dependencies and integration points: used by page-skip logic in `rts_btree_walk.c` and update/on-disk processing in `rts_btree.c`. It depends on checkpoint aggregate metadata semantics, transaction snapshot helpers, history-store URI/handle detection, and recovery flags such as `WT_CHECK_RECOVERY_FLAG_TXNID`.

Risks: false negatives leave unstable content unread; false positives cause extra page reads and can instantiate deleted pages unnecessarily. History-store max timestamp rules differ from data-store rules, so sharing logic without the HS branch would miss prepared records. Recovery snapshot handling must match checkpoint metadata generation.

Test signals: validate page-needs-abort for in-memory trees, replace and multiblock reconciliation, instantiated fast-deleted pages, on-page/off-page addresses, prepared aggregate flags, recovery newest transaction checks, history-store aggregate timestamp behavior, and no-snapshot recovery visibility.
