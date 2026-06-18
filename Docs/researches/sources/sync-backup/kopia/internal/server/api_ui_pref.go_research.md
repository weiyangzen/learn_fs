# sources/sync-backup/kopia/internal/server/api_ui_pref.go

Purpose: stores and retrieves UI preferences for the server.

Important APIs/types/functions: `getUIPreferencesOrEmpty`, `handleGetUIPreferences`, and `handleSetUIPreferences`.

Control flow: get reads the preferences JSON file if configured and returns empty preferences when missing. Set decodes preferences and writes them to the configured file.

State and persistence behavior: persists JSON preferences to `Options.UIPreferencesFile`; no repository data is required.

Dependencies and integration points: available even when not connected to a repository through `handleUIPossiblyNotConnected`.

Risks and test signals: malformed files and write permission errors should return API errors. Tests cover get/set behavior.
