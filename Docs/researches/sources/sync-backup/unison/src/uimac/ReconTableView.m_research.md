<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconTableView.m -->
# sources/sync-backup/unison/src/uimac/ReconTableView.m

Source read: complete file, 298 lines, 7716 bytes, sha256 `3385741ea016899c`.

Purpose: Implements selection helpers, keyboard shortcuts, command validation, row auto-expansion, and action dispatch for the reconciliation outline table.

Important APIs/types/functions: Category methods convert selected rows to objects and back, estimate row capacity, and expand children if space permits. `ReconTableView` implements validation, `doAction:`, `doIgnore:`, all IB action methods, `keyDown:`, `canDiffSelection`, and highlight color override.

Implementation inventory: discovered Objective-C/C callback methods include `selectedObjects, setSelectedObjects, selectedObjectEnumerator, rowCapacityWithoutScrolling, _canAcceptRowCountWithoutScrolling, _expandChildrenIfSpace, expandChildrenIfSpace, editable, setEditable, validateItem, validateMenuItem, validateToolbarItem, doIgnore, ignorePath, ignoreExt, ignoreName, doAction, copyLR, copyRL, leaveAlone, forceOlder, forceNewer, selectConflicts, revert, merge, showDiff, keyDown, canDiffSelection` and more.

Control flow: Commands are enabled only when the table is editable, with diff/merge further requiring diff-capable selection. Ignore commands call selected items, ask `MyController updateForIgnore:` for the replacement selection, and reload. Direction commands call selected items, advance to the next row for single selections, and reload. Keyboard shortcuts map `>`, right arrow, `<`, left arrow, `?`, and `/` to common actions.

State and persistence behavior: Stores editability; selection and expansion are owned by the outline view. It relies on model mutations inside `ReconItem`.

Dependencies and integration points: Depends on `ReconItem`, `MyController`, AppKit toolbar/menu validation protocols, and private `_highlightColorForCell:` behavior.

Risks: Several `while (item = [e nextObject])` loops rely on intentional assignment. Selection after ignore assumes the replacement item remains visible. Private highlight override may be fragile. `canDiffSelection` returns YES for empty selection, though callers usually check row count for show diff.

Test signals: Keyboard/action tests for single and multi-selection, ignore flows, conflict selection, diff enablement, row advancement, and selection preservation after table reload/sort.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ReconTableView.m -->
