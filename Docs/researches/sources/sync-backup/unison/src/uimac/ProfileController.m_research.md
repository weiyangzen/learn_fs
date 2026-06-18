<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileController.m -->
# sources/sync-backup/unison/src/uimac/ProfileController.m

Source read: complete file, 90 lines, 2580 bytes, sha256 `e005e27a706c2d16`.

Purpose: Implements profile discovery and table data-source behavior for the Mac UI profile chooser.

Important APIs/types/functions: Global `unisonDirectory()` calls OCaml, `initProfiles` scans files, `awakeFromNib` initializes and selects defaults, and table methods return row count/name values.

Implementation inventory: discovered Objective-C/C callback methods include `initProfiles, awakeFromNib, numberOfRowsInTableView, tableView, selected, tableView, getProfiles`.

Control flow: The controller reads directory contents, filters names ending in `.prf`, strips extensions, records `default`, sorts names, selects the first row and then default if available, and reloads the table.

State and persistence behavior: Owns the retained `profiles` array. `defaultIndex` is reset on each scan. It does not persist data itself.

Dependencies and integration points: Depends on `NSFileManager`, `NSTableView`, and OCaml `unisonDirectory`. It integrates with `MyController` for open/create flows.

Risks: The `defaultIndex` is captured before sorting, so selecting it after sort can select the wrong row. There is no `dealloc` releasing `profiles`. Directory read failures silently produce an empty list.

Test signals: Run profile-list tests with unsorted filenames where `default` would move after sort, missing directories, and profile creation refresh.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ProfileController.m -->
