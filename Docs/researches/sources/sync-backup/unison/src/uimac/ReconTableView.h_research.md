<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconTableView.h -->
# sources/sync-backup/unison/src/uimac/ReconTableView.h

Source read: complete file, 43 lines, 1180 bytes, sha256 `6f701753a49001fd`.

Purpose: Declares the reconciliation outline view subclass and an `NSOutlineView` category for selected-object and auto-expansion helpers.

Important APIs/types/functions: Public actions cover ignore by path/ext/name, copy left-right/right-left, skip, force older/newer, select conflicts, revert, merge, show diff, validation, and editability. The category adds `selectedObjects`, `setSelectedObjects:`, `selectedObjectEnumerator`, and `expandChildrenIfSpace`.

Implementation inventory: discovered Objective-C/C callback methods include `editable, setEditable, validateItem, validateMenuItem, validateToolbarItem, ignorePath, ignoreExt, ignoreName, copyLR, copyRL, leaveAlone, forceOlder, forceNewer, selectConflicts, revert, merge, showDiff, canDiffSelection, selectedObjects, selectedObjectEnumerator, setSelectedObjects, expandChildrenIfSpace`.

Control flow: `MyController` uses this as the outline view for recon items; toolbar/menu/key events call actions here, which in turn delegate to selected `ReconItem` objects.

State and persistence behavior: Only an `editable` flag is stored in the table view. Selection state remains AppKit-owned.

Dependencies and integration points: Depends on AppKit `NSOutlineView`, `ReconItem`, and `MyController` in implementation.

Risks: Action availability depends on `editable`; callers must update it when sync state changes. Category methods assume data source implements outline child APIs.

Test signals: Validate menu/toolbar enablement before scan, after scan, during sync, and after sync; exercise multiple selection and auto-expansion.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconTableView.h -->
