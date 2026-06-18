# sources/sync-backup/kopia/internal/server/api_notification_profile_test.go

Purpose: integration-tests notification profile API lifecycle.

Important APIs/types/functions: `TestNotificationProfile`.

Control flow: starts a test server, uses API client calls to create notification profiles, retrieve and list them, run test notification behavior, and delete profiles.

State and persistence behavior: profile state persists in the temporary test repository during the test.

Dependencies and integration points: validates server routing, repository writes, auth/CSRF, and serverapi payload shapes.

Risks and test signals: external notification transports are usually mocked or inert; real transport failures require separate tests.
