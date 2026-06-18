# sources/sync-backup/syncthing/cmd/dev/stfindignored/main.go

Purpose: development utility that lists ignored files under a Syncthing folder root using the project's real ignore engine.

Important APIs/types/functions: uses `fs.NewFilesystem`, `fs.NewWalkFilesystem`, `ignore.New`, `Load(".stignore")`, `Walk`, and `Match(path).IsIgnored()`.

Control flow: defaults root to `.`, creates a walkable filesystem rooted there, loads `.stignore`, walks all paths, warns and skips directories on walk errors, and prints paths that match ignore rules.

State and persistence behavior: read-only filesystem traversal. Runtime state is the loaded ignore matcher.

Dependencies/integration: exercises Syncthing's filesystem abstraction and ignore parser/matcher, so behavior should match application ignore semantics more closely than shell glob tools.

Risks/test signals: fatal if `.stignore` is missing or invalid; warnings skip inaccessible subtrees. Signal is printed ignored paths for a real folder.
