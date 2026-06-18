<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileTableView.m -->
# sources/sync-backup/unison/src/uimac/ProfileTableView.m

Source read: complete file, 36 lines, 894 bytes, sha256 `49fd84af95629fcf`.

Purpose: Adds keyboard activation and custom highlight color to the profile table.

Important APIs/types/functions: Overrides `keyDown:` and private `_highlightColorForCell:`.

Implementation inventory: discovered Objective-C/C callback methods include `keyDown, _highlightColorForCell`.

Control flow: Empty character events pass through. Return calls `[myController openButton:self]`; other keys delegate to the superclass. Highlight color changes depending on first responder/key-window state to match the reconciliation table style.

State and persistence behavior: Uses only table/window focus state and the controller outlet.

Dependencies and integration points: Depends on `MyController` and AppKit private highlight override behavior.

Risks: `_highlightColorForCell:` is a private/undocumented override and may break on newer AppKit. Return key behavior depends on characters rather than key codes.

Test signals: Keyboard smoke tests for Return, arrow navigation, empty-character function keys, and selected-row colors in active/inactive windows.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileTableView.m -->
