<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/UnisonToolbar.h -->
# sources/sync-backup/unison/src/uimac/UnisonToolbar.h

Source read: complete file, 33 lines, 1045 bytes, sha256 `c8d73bf5120708f0`.

Purpose: Declares the Mac UI toolbar controller subclass that swaps toolbar items according to the current main view.

Important APIs/types/functions: Initializer takes a controller and reconciliation table. Delegate methods create items and expose default/allowed identifiers. `setView:` changes item layout, and `takeTableModeView:` installs the segmented table-mode control.

Implementation inventory: discovered Objective-C/C callback methods include `toolbar, itemIdentifiersForView, toolbarDefaultItemIdentifiers, toolbarAllowedItemIdentifiers, setView, takeTableModeView`.

Control flow: `MyController` creates the toolbar and calls `setView:` whenever the UI transitions between profile, preferences, connecting, and updates states.

State and persistence behavior: Tracks target table/controller, current view name, and retained table-mode view.

Dependencies and integration points: Depends on AppKit `NSToolbar`, `ReconTableView`, and `MyController` actions.

Risks: Toolbar identifiers are string literals in the implementation, so view names/actions must stay synchronized with nib/controller methods.

Test signals: Switch every main view and verify toolbar items, icons, targets, and validation state.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/UnisonToolbar.h -->
