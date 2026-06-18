<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileTableView.h -->
# sources/sync-backup/unison/src/uimac/ProfileTableView.h

Source read: complete file, 11 lines, 163 bytes, sha256 `9f99e0686d50d9bc`.

Purpose: Declares a profile chooser table subclass that forwards Return key activation to `MyController`.

Important APIs/types/functions: Contains one outlet to `MyController`; behavior is implemented by overriding `keyDown:` and highlight color in the `.m` file.

Control flow: When the profile table is first responder, Return opens the selected profile instead of merely editing/selecting.

State and persistence behavior: No persistent state; only the outlet matters.

Dependencies and integration points: Depends on `NSTableView` and `MyController`.

Risks: Missing outlet wiring makes Return key activation a no-op or crash depending on nil messaging expectations.

Test signals: Select a profile and press Return, plus verify normal key events still pass to `NSTableView`.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileTableView.h -->
