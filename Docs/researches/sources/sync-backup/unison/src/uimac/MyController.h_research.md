<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/MyController.h -->
# sources/sync-backup/unison/src/uimac/MyController.h

Source read: complete file, 146 lines, 3941 bytes, sha256 `27b5ecbd3dd0504f`.

Purpose: Declares the central Cocoa controller for the Unison Mac UI: profile selection, profile creation, connection, reconciliation table, sync execution, progress, diff display, preferences, notifications, and validation.

Important APIs/types/functions: Exports many IB actions and delegate methods, including `chooseProfiles`, `createButton:`, `openButton:`, `connect:`, `syncButton:`, `updateReconItems:`, `displayDetails:`, `validateItem:`, and font/profile/preference actions. It also exposes `reconItems` for `ReconTableView`.

Implementation inventory: discovered Objective-C/C callback methods include `init, awakeFromNib, chooseProfiles, createButton, saveProfileButton, cancelProfileButton, profile, profileSelected, showPreferences, restartButton, rescan, openButton, connect, raisePasswordWindow, controlTextDidEndEditing, endPasswordWindow, afterOpen, syncButton, tableModeChanged, initTableMode, reconItems, updateForChangedItems, updateReconItems, updateForIgnore, statusTextSet, diffViewTextSet, displayDetails, clearDetails` and more.

Control flow: The controller is loaded from the main nib, wires multiple view panels into one main window, and switches toolbar/window state as the workflow moves from profile choice to preferences, connecting, update review, and synchronization.

State and persistence behavior: Holds outlets, selected profile name, `reconItems`, `rootItem`, OCaml preconnection state, sync flags, password wait flag, timers, table mode, font target, and batch/quit state.

Dependencies and integration points: Depends on every local UI class (`ProfileController`, `PreferencesController`, `NotificationController`, `ReconItem`, `ReconTableView`, `UnisonToolbar`, cells/views) plus `Bridge.h` for OCaml values.

Risks: The large controller surface couples UI state, OCaml callbacks, and table model state tightly. Many outlets are implicitly required by the nib; missing connections can fail at runtime rather than compile time.

Test signals: Nib loading, profile selection/creation, toolbar validation, OCaml callback smoke tests, password dialog, sync completion, batch timeout, and table-mode persistence should all exercise this header's contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/MyController.h -->
