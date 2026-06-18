<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/NotificationController.h -->
# sources/sync-backup/unison/src/uimac/NotificationController.h

Source read: complete file, 18 lines, 394 bytes, sha256 `268b2193bf3512d7`.

Purpose: Declares a small notification delegate/controller for scan and sync completion notifications.

Important APIs/types/functions: Exports `updateFinishedFor:` and `syncFinishedFor:` and conforms to `NSApplicationDelegate` and `NSUserNotificationCenterDelegate`.

Implementation inventory: discovered Objective-C/C callback methods include `updateFinishedFor, syncFinishedFor`.

Control flow: The implementation installs itself as the user notification center delegate at nib wakeup and sends notifications when `MyController` reports completion events.

State and persistence behavior: No explicit instance state; notification center delegate registration is global process state.

Dependencies and integration points: Depends on Cocoa `NSUserNotificationCenter`, which is deprecated on modern macOS in favor of UserNotifications.

Risks: Deprecated API can affect future builds; no authorization/error handling is present. Delegate lifetime depends on nib ownership.

Test signals: Trigger scan and sync completion with the app foreground/background and verify notifications present with the expected profile text.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/NotificationController.h -->
