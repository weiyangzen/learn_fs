<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/PreferencesController.h -->
# sources/sync-backup/unison/src/uimac/PreferencesController.h

Source read: complete file, 20 lines, 548 bytes, sha256 `9d70b8a4c35881a2`.

Purpose: Declares the controller for creating/editing profile preferences in the Mac UI.

Important APIs/types/functions: Outlets represent profile name, first root, local/remote toggles, and remote user/host/path fields. Methods are `reset`, `validatePrefs`, `anyEnter:`, `localClick:`, and `remoteClick:`.

Implementation inventory: discovered Objective-C/C callback methods include `anyEnter, localClick, remoteClick, validatePrefs, reset`.

Control flow: The main controller presents this panel during profile creation; validation constructs a Unison root pair and asks OCaml to initialize the profile.

State and persistence behavior: State lives in text fields and radio button cells. There is no independent model object.

Dependencies and integration points: Depends on Cocoa controls and `PreferencesController.m`'s OCaml bridge use.

Risks: Validation policy is in UI code and only checks emptiness, not duplicate profile names or path syntax.

Test signals: Exercise local/remote toggle enablement, empty-field validation, and successful profile creation with local and SSH roots.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/PreferencesController.h -->
