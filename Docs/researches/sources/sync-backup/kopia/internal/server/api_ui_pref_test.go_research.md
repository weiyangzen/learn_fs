# sources/sync-backup/kopia/internal/server/api_ui_pref_test.go

Purpose: tests UI preference API persistence.

Important APIs/types/functions: `TestUIPreferences`.

Control flow: starts a test server with a preferences file, gets default preferences, sets new preferences, and verifies subsequent retrieval.

State and persistence behavior: writes a temporary JSON preferences file.

Dependencies and integration points: validates not-connected-capable UI endpoint handling plus file persistence.

Risks and test signals: malformed existing JSON and filesystem permission failures need separate tests.
