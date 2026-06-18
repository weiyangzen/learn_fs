# sources/sync-backup/git-lfs/script/upload

Purpose: orchestrates GitHub draft release creation/update, asset upload/download, final signing, body generation, and verification.

Important functions: `say`, `abort`, `uri_encode`, custom `curl`, `categorize_os`, `categorize_arch`, `categorize_asset`, `content_type`, `format_release_json`, `create_release`, `patch_release`, `release_files`, `finalize_body_message`, `filter_files`, `upload_assets`, `download_assets`, `verify_assets`, `extract_changelog`, `finalize`, `usage`, `sanity_check`, and `main`.

Control flow: parses `--inspect`, `--skip-verify`, and `--finalize`. Normal mode extracts changelog, generates a release body with PackageCloud links and SHA-256 hashes, creates or reuses a draft release, uploads new assets, then verifies downloaded signatures. Finalize mode downloads release assets, optionally opens a shell for inspection, regenerates signed hash manifests, patches the release body, uploads final signature assets, and verifies unless skipped.

State/persistence behavior: uses a temp workdir removed by trap, reads `bin/releases`, creates/patches GitHub releases, uploads assets to GitHub, downloads assets for verification, and generates signed manifests using local GPG keys.

Dependencies/integration: GitHub API, `GITHUB_TOKEN` or `.netrc`, curl, jq, ruby, shasum, gpg, optional sha3sum/b2sum, `script/distro-tool`, and `script/hash-files`.

Risks: release discovery searches by release name; repeated API listing can race or become slow. Filename globs encode supported asset patterns. Final signing depends on local GPG configuration. Duplicate asset filtering only compares names already present.

Test signals: successful draft/final release with expected labels/content types, signed manifests verifying after download, and body text with correct changelog/package/hash sections.
