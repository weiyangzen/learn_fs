<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/MyController.m -->
# sources/sync-backup/unison/src/uimac/MyController.m

Source read: complete file, 1263 lines, 43955 bytes, sha256 `8de43fce1ad71672`.

Purpose: Implements the main Unison Mac GUI controller and OCaml callback entry points. It coordinates profile selection/creation, connection to the OCaml engine, reconciliation item model construction, action validation, sync execution, progress/diff/status rendering, notifications, and shutdown behavior.

Important APIs/types/functions: Important Objective-C methods include `awakeFromNib`, `chooseProfiles`, profile save/cancel/open actions, `connect:`, `raisePasswordWindow:`, `afterOpen`, `syncButton:`, `doSync`, `afterUpdate:`, `afterSync:`, `updateReconItems:`, table data source/delegate methods, validation methods, font/preference handlers, and helper view-resize methods. C entry points exported to OCaml include `unisonInit1Complete`, `unisonInit2Complete`, `syncComplete`, `reloadTable`, `displayStatus`, `displayGlobalProgress`, `displayDiff`, `displayDiffErr`, `fatalError`, and `warnPanel`.

Implementation inventory: discovered Objective-C/C callback methods include `trim, applicationShouldTerminateAfterLastWindowClosed, init, applicationWillTerminate, awakeFromNib, checkOpenProfileChanged, chooseFont, changeFont, updateFontDisplay, chooseProfiles, createButton, saveProfileButton, cancelProfileButton, profile, profileSelected, showPreferences, restartButton, rescan, openButton, updateToolbar, updateTableViewWithReset, updateProgressBar, updateTableViewSelection, outlineViewSelectionDidChange, connect, unisonInit1Complete, unisonInit1Complete, raisePasswordWindow` and more.

Control flow: `awakeFromNib` configures toolbar, views, cells, fonts, profile box, and initial profile selection. Opening a profile calls OCaml `unisonInit1`, waits for callback completion, possibly raises a password sheet, then calls `afterOpen` to initialize scanning. OCaml update callbacks deliver reconciliation data; `updateReconItems:` builds `LeafReconItem` and `ParentReconItem` structures, updates the outline, expands rows, and refreshes detail/progress state. User toolbar/table actions call into `ReconItem` to update OCaml directions/ignore rules. `syncButton:` either starts `doSync` or handles post-sync/batch quit logic, and OCaml `syncComplete` returns the UI to an after-sync state.

State and persistence behavior: Maintains current view, profile, syncability flags, batch mode, table nesting preference, font preferences, preconnection handle, root and flattened reconciliation items, progress bar values, timeout alert/timer, and password wait state. It persists user preferences through `NSUserDefaults` for opening profiles and fonts; synchronization state itself lives in OCaml and is reflected into UI objects.

Dependencies and integration points: Depends on AppKit, `Bridge`/OCaml named callbacks (`unisonInit1`, `unisonInit2`, `unisonSynchronize`, profile/path/diff/status functions), local table/cell/toolbar classes, notification delivery, user defaults, and bundled icon assets.

Risks: High coupling and manual memory management create leak/dangling risks. UI updates must happen on the main thread after OCaml callbacks; callback signatures are vararg/stringly typed. Batch timeout and `shouldExitAfterWarning` paths can exit unexpectedly if warning state is mishandled. Sorting/selection relies on model object identity and cached sort keys.

Test signals: End-to-end GUI tests should cover profile open/create, remote/local preference validation, password prompt, scan completion, conflicts and direction changes, ignore rules, diff display, sync completion notification, batch timeout, font changes, toolbar/menu validation, and fatal/warn OCaml callbacks.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/MyController.m -->
