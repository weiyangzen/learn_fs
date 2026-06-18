<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifyprofile/notification_profile.go -->
# sources/sync-backup/kopia/notification/notifyprofile/notification_profile.go

- Purpose: Manages repository-stored notification sender profiles.
- Important APIs/types/functions: `Config`, `Summary`, `ListProfiles`, `ErrNotFound`, `GetProfile`, `SaveProfile`, `DeleteProfile`, `labelsForProfileName`.
- Control flow: List finds all notification profile manifests and loads each config. Get finds manifests for one profile and loads latest. Save replaces manifests with matching labels. Delete removes all matching manifests.
- State and persistence: Profiles persist as repository manifests with type `notificationProfile` and `profile` labels.
- Dependencies and integration points: Integrates `sender.MethodConfig`, repository manifests, notification send selection, and logging.
- Risks and edge cases: Profile name validation is not enforced here; malformed sender configs are handled later by sender construction.
- Test signals: Indirectly exercised by server remote notification test; no direct profile unit test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifyprofile/notification_profile.go -->
