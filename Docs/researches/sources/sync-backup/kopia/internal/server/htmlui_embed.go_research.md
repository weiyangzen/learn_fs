# sources/sync-backup/kopia/internal/server/htmlui_embed.go

Purpose: exposes the bundled HTML UI filesystem when the `nohtmlui` build tag is not set.

Important APIs/types/functions: `AssetFile`.

Control flow: delegates to `htmluibuild.AssetFile()`.

State and persistence behavior: serves embedded/static build assets; no mutation.

Dependencies and integration points: `Server.ServeStaticFiles` uses this filesystem to serve the UI and patch `index.html`.

Risks and test signals: build dependency on generated `htmluibuild` assets must be available for normal builds.
