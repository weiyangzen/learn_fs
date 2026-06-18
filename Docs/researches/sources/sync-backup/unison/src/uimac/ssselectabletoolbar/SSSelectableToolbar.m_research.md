<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.m -->
# sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.m

Source read: complete file, 157 lines, 5155 bytes, sha256 `b5ed19caa6931c0d`.

Purpose: Implements toolbar-driven content switching for preference-style windows.

Important APIs/types/functions: `initWithIdentifier:`, `awakeFromNib`, `selectDefaultItem:`, `setSelectedItemIdentifier:`, `selectItemWithIndex:`, `selectableItemIndexToMainIndex:`, and `itemWithIdentifier:` are the main methods.

Implementation inventory: discovered Objective-C/C callback methods include `initWithIdentifier, dealloc, toolbarItemClicked, selectDefaultItem, awakeFromNib, itemWithIdentifier, setSelectedItemIdentifier, selectItemWithIndex, selectableItemIndexToMainIndex`.

Control flow: Initialization creates a blank view. At nib wakeup, selectable toolbar items get a dummy target/action so they are clickable, and the toolbar registers for the window becoming key. Selecting an item finds its linked view, computes a new window frame preserving toolbar height, temporarily sets the blank content view, animates resizing, installs the linked view, updates the title, and focuses the linked view's `nextKeyView` if present.

State and persistence behavior: Owns `blankView` and retained `window`; selection state is held by `NSToolbar`. Default selection is a numeric index over selectable items.

Dependencies and integration points: Depends on `SSSelectableToolbarItem`, AppKit window/content sizing, and notification center.

Risks: The notification observer is removed only after default selection; if the toolbar deallocs before notification, there is observer risk on older runtimes. `setSelectedItemIdentifier:` assumes linked views have meaningful frames. Window release in `dealloc` must match property ownership from nib binding.

Test signals: Open the preferences window as a normal window and sheet, switch every toolbar item, verify animated resize/title/focus, and close before/after the key-window notification.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.m -->
