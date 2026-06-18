<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_child.c -->
# sources/storage-engines/wiredtiger/src/reconcile/rec_child.c

## Purpose
Determines how an internal-page reconciliation should represent each child reference: original address, modified replacement, proxy fast-delete cell, ignore, or error.

## Important APIs, Types, and Functions
`__wti_rec_child_modify` is the exported decision function. `__rec_child_deleted` handles `WT_REF_DELETED` and instantiated fast-truncate cases. Key state is returned through `WTI_CHILD_MODIFY_STATE`.

## Control Flow
For disk refs, it keeps the original address. Deleted refs are locked and evaluated for visibility, global visibility, prepared state, precise checkpoint timestamp, and previously-selected proxy state. Memory refs may get hazard pointers and inspect `page->modify->rec_result`; instantiated deleted pages are reevaluated as fast deletes. Modified children can be empty, multiblock, or replace. Split/locked states cause wait/retry or diagnostic errors depending on eviction/checkpoint context.

## State and Persistence Behavior
May free globally visible deleted child blocks and clear `ref->page_del`. May set `page_del->selected_for_write` and `r->leave_dirty`. It can force full images instead of deltas to avoid parent deltas referencing freed proxy cells.

## Dependencies and Integration Points
Central to internal-page reconciliation, checkpoint, eviction, fast truncate, rollback-to-stable safety, delta building, page hazard management, and block freeing.

## Risks and Edge Cases
Prepared truncates and uncommitted deletes require strict ordering and locking. Visibility decisions differ for checkpoints, eviction, and no-snapshot reconciliation. Mishandling instantiated deletes can resurrect freed pages or lose truncates.

## Test Signals
Fast-truncate checkpoint/eviction tests, prepared truncate visibility tests, precise checkpoint timestamp tests, delta-vs-full-image regressions, and concurrent page-state transition stress are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/reconcile/rec_child.c -->
