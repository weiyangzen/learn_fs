<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileController.h -->
# sources/sync-backup/unison/src/uimac/ProfileController.h

Source read: complete file, 20 lines, 658 bytes, sha256 `d435c51ad1c7b9a1`.

Purpose: Declares the profile-list controller backing the initial profile selection table.

Important APIs/types/functions: Exports `initProfiles`, table data source methods, `selected`, `tableView`, and `getProfiles`.

Implementation inventory: discovered Objective-C/C callback methods include `initProfiles, numberOfRowsInTableView, tableView, selected, tableView, getProfiles`.

Control flow: At nib wakeup the implementation asks OCaml for the Unison directory, scans `.prf` files, sorts them, and selects `default` when available.

State and persistence behavior: Stores a mutable profile-name array and the index of the default profile.

Dependencies and integration points: Depends on Cocoa `NSTableView` and the bridge function that supplies the Unison directory.

Risks: `defaultIndex` uses an unsigned type with `-1` sentinel, which relies on wraparound semantics. The selected index is computed before sorting and can become stale.

Test signals: Populate a temporary Unison directory with several `.prf` files, including `default.prf`, and verify table rows, sorting, and selected profile.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileController.h -->
