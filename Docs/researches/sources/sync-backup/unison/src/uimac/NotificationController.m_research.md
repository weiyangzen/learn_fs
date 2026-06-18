<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/NotificationController.m -->
# sources/sync-backup/unison/src/uimac/NotificationController.m

Source read: complete file, 50 lines, 1480 bytes, sha256 `2ef3c5fcf72ae890`.

Purpose: Implements simple macOS user notifications for finished scan and synchronization events.

Important APIs/types/functions: `awakeFromNib`, `updateFinishedFor:`, `syncFinishedFor:`, delegate `shouldPresentNotification:`, and file-local `simpleNotify` are the relevant functions.

Implementation inventory: discovered Objective-C/C callback methods include `awakeFromNib, updateFinishedFor, syncFinishedFor, userNotificationCenter`.

Control flow: Completion methods call `simpleNotify` with a title and profile-aware format. `simpleNotify` allocates `NSUserNotification`, fills title/body/sound, and delivers it through the default center. The delegate always returns YES so notifications appear even while the app is active.

State and persistence behavior: Only transient notification objects are created. The function leaks the allocated notification under manual reference counting because it is never released.

Dependencies and integration points: Depends on AppKit/Foundation notification APIs and `MyController` calls after update/sync completion.

Risks: Deprecated notification API, missing release, no user authorization handling, and no localization of notification strings.

Test signals: Manual or UI automation should verify foreground presentation, notification text for profile names with spaces, and behavior on macOS versions where `NSUserNotification` is deprecated.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/NotificationController.m -->
