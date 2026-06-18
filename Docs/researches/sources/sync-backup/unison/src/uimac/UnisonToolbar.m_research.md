<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/UnisonToolbar.m -->
# sources/sync-backup/unison/src/uimac/UnisonToolbar.m

Source read: complete file, 216 lines, 9309 bytes, sha256 `a8526d92e1134c86`.

Purpose: Implements the Unison toolbar item factory and per-view toolbar layouts.

Important APIs/types/functions: Defines identifiers for Quit/Open/New/Go/Cancel/Save/Restart/Rescan/direction/Merge/Skip/Diff/TableMode. Implements toolbar delegate item creation, default/allowed identifiers, `itemIdentifiersForView:`, `setView:`, and `takeTableModeView:`.

Implementation inventory: discovered Objective-C/C callback methods include `takeTableModeView, toolbar, itemIdentifiersForView, toolbarDefaultItemIdentifiers, toolbarAllowedItemIdentifiers, setView`.

Control flow: Item creation maps identifiers to labels, bundled `.tif` images, targets, and actions on either `NSApp`, `MyController`, or `ReconTableView`. `setView:` diffs desired identifiers against current toolbar items, replacing/inserting/removing as needed. The updates view adds sync/reconcile commands and the table-mode segmented view.

State and persistence behavior: Stores retained table-mode view and current view string. Toolbar autosave/customization is disabled.

Dependencies and integration points: Depends on toolbar image assets, `MyController` action names, `ReconTableView` actions, and AppKit toolbar validation.

Risks: No `dealloc` releases `tableModeView`. `currentView` is assigned, not copied/retained, though callers use stable string literals. Missing images silently produce blank toolbar items.

Test signals: View transition tests should verify item order and targets. Bundle validation should check every `toolbar/*.tif` asset exists and validation disables table actions while not editable.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/UnisonToolbar.m -->
