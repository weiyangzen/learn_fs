# sources/user-network-fs/rclone/bin/fetch-gui-dist.sh

Purpose: fetches the latest `dist.zip` from `rclone/rclone-web` GitHub releases into `cmd/gui/dist.zip` and records the release tag in `cmd/gui/dist.tag`. It supports `--commit` to commit changed GUI assets.

Control flow: parses arguments, optionally adds GitHub token auth, calls the releases API with retrying curl, extracts `tag_name` and the `dist.zip` asset URL via Python JSON snippets, skips if local zip/tag already match, downloads via a temp file, atomically moves it into place, writes tag, and optionally stages/commits. State changes are the embedded GUI zip/tag and optional git commit. Risks include relying on latest release mutability, GitHub rate limits, Python availability, partial state if tag write succeeds but commit fails, and zip contents not independently verified. Test signal is command success and reproducible build behavior.
