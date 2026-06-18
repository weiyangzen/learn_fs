# Research: sources/sync-backup/syncthing/script/copyrights.go

## sources/sync-backup/syncthing/script/copyrights.go

Purpose: maintenance generator that updates third-party copyright notices in the GUI about modal based on modules used by `cmd/syncthing`.

Important APIs/types/functions: `CopyrightNotice`, `Type` enum, hard-coded `copyrightMap`/`urlMap`, `getModules`, `parseCopyrightNotices`, `parseGitHubURL`, `getLicenseText`, `extractCopyrights`, `defaultCopyright`, and `write`.

Control flow: parses current notices from `aboutModalView.html`, lists modules and packages via `go list`, matches existing notices to live modules, marks unused notices for removal, adds new module notices, resolves known or GitHub license copyrights for new modules, then rewrites the HTML list in sorted order while preserving JS/static notices.

State and persistence: writes `gui/default/syncthing/core/aboutModalView.html`. Network state may be read from GitHub API, optionally authenticated by `GITHUB_TOKEN`.

Dependencies and integration: Go toolchain, module graph, HTML parser, GitHub API. Risks include rate limiting, fragile matching by substring, default copyright fallback quality, and generated HTML churn. Test signal is the resulting diff and successful command execution.
