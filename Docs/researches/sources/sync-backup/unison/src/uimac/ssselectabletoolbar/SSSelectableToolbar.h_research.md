<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.h -->
# sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.h

Source read: complete file, 27 lines, 886 bytes, sha256 `639fce8865cee3dc`.

Purpose: Declares a reusable selectable toolbar that swaps a window's content view when selectable toolbar items are chosen.

Important APIs/types/functions: Properties are retained `window` outlet and assign `defaultItemIndex`. Methods include `itemWithIdentifier:`, `selectItemWithIndex:`, and `selectableItemIndexToMainIndex:`.

Implementation inventory: discovered Objective-C/C callback methods include `itemWithIdentifier, selectItemWithIndex, selectableItemIndexToMainIndex`.

Control flow: The implementation waits for the window to become key, selects a default item, and then changes the window content and size on toolbar selection.

State and persistence behavior: Tracks the target window, a blank placeholder view, and default selectable item index.

Dependencies and integration points: Depends on AppKit `NSToolbar` and custom `SSSelectableToolbarItem` linked views.

Risks: A missing `window` outlet prevents content switching. Index methods count only selectable toolbar items, which differs from raw toolbar item indexes.

Test signals: Nib-load with multiple selectable items, default selection, and index mapping around spacers/nonselectable items.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ssselectabletoolbar/SSSelectableToolbar.h -->
