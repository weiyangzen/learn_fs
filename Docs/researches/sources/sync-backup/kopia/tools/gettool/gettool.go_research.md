# sources/sync-backup/kopia/tools/gettool/gettool.go

Purpose: `gettool` is a small Kopia build helper that downloads pinned, platform-specific third-party tools from upstream release archives. It centralizes tool URL templates, OS/architecture translations, extraction stripping, checksum verification, and checksum regeneration.

Important APIs/types/functions: `ToolInfo` stores a URL template plus OS/arch maps and unsupported platform rules. `ToolInfo.actualURL` expands `VERSION`, `GOOS`, `GOARCH`, and `EXT`. Global `tools` defines linter, Hugo, gotestsum, Kopia, rclone, goreleaser, git-chglog, and node. `parseEmbeddedChecksums` reads embedded `checksums.txt`. `downloadTool` executes normal, `--test-all`, or `--regenerate-checksums` modes.

Control flow: `main` parses flags, loads embedded checksums, then loops over comma-separated `tool:version` specs. Normal mode downloads one archive for selected `--goos/--goarch`. `--test-all` probes a fixed platform matrix and counts failures. `--regenerate-checksums` preserves existing checksums and downloads missing ones so `autodownload.InvalidChecksumError` can populate discovered hashes.

State/persistence: writes tools into `--output-dir`; optional checksum regeneration writes the sorted URL-to-hash lines to the requested file. It exits fatally on unsupported specs or normal-mode download failures.

Dependencies/integration: uses `embed`, `flag`, runtime platform values, and package `tools/gettool/autodownload`. `tools.mk` invokes it for local/CI tool installation and checksum maintenance.

Risks/test signals: platform metadata is hardcoded, so upstream naming changes break downloads. `parseEmbeddedChecksums` assumes each line contains `": "`. Regeneration has side effects both in output directories and checksum files. Test signals are the Make targets `verify-all-tool-checksums` and `regenerate-checksums`.
