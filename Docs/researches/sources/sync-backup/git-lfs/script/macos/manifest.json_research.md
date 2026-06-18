# sources/sync-backup/git-lfs/script/macos/manifest.json

Purpose: manifest for macOS notarization tooling.

Important fields: `apple_id.password` reads from `DARWIN_DEV_PASS`; `notarize.path` targets `git-lfs`; `bundle_id` is `com.github.git-lfs`; `staple` is false.

Control flow: declarative JSON, not executable.

State/persistence behavior: no local state. It instructs notarization tooling how to submit the Git LFS binary and where to obtain credentials.

Dependencies/integration: pairs with macOS release/notarization scripts and CI secrets.

Risks: depends on environment secret naming and assumes the artifact path is exactly `git-lfs`. `staple: false` means notarization tickets are not stapled by this manifest.

Test signals: successful notarization submission in macOS release jobs.
