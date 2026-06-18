# sources/sync-backup/kopia/internal/server/api_notification_profile.go

Purpose: manages notification profiles through server APIs.

Important APIs/types/functions: `handleNotificationProfileCreate`, `handleNotificationProfileTest`, `handleNotificationProfileGet`, `handleNotificationProfileDelete`, and `handleNotificationProfileList`.

Control flow: handlers decode profile/test requests, operate in repository write sessions where mutations are needed, store or remove notification profile definitions, list configured profiles, and send a test notification for validation.

State and persistence behavior: notification profiles persist as repository configuration/manifest data; test sends external notification side effects depending on configured provider.

Dependencies and integration points: integrates `serverapi` requests, repository writer sessions, and Kopia notification packages.

Risks and test signals: profile names are route parameters and must align with stored names; test notification can fail due to external transport settings. Tests cover create/get/list/delete and test paths.
