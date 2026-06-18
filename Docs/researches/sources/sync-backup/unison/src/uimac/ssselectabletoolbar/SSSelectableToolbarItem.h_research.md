<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.h -->
# sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.h

Source read: complete file, 19 lines, 345 bytes, sha256 `7b642afa5b415295`.

Purpose: Declares an `NSToolbarItem` subclass that associates a toolbar item with an `NSView` to display when selected.

Important APIs/types/functions: The single retained IBOutlet property is `linkedView`.

Control flow: `SSSelectableToolbar` reads `linkedView` from selected items and installs it as the window content view.

State and persistence behavior: Owns the linked view reference.

Dependencies and integration points: Depends on Cocoa and Interface Builder wiring.

Risks: Missing linked view wiring makes selection change only the toolbar state without swapping content.

Test signals: Inspect nib connections and switch every toolbar item to verify each has a non-nil linked view.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbarItem.h -->
