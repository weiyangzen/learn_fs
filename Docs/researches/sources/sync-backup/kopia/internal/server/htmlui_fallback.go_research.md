# sources/sync-backup/kopia/internal/server/htmlui_fallback.go

Purpose: fallback HTML UI asset provider for `nohtmlui` builds.

Important APIs/types/functions: embedded `data` filesystem and `AssetFile`.

Control flow: returns an `http.FileSystem` backed by minimal embedded fallback content.

State and persistence behavior: read-only embedded assets.

Dependencies and integration points: allows server builds without full UI assets while keeping static serving code functional.

Risks and test signals: fallback UI is limited; build-tag tests should ensure both asset providers compile.
