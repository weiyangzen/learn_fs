# sources/sync-backup/git-lfs/script/notarize

Purpose: submits a single artifact to Apple notarization without echoing credentials into CI logs.

Important command: `xcrun notarytool submit "$1" --apple-id "$DARWIN_DEV_USER" --password "$DARWIN_DEV_PASS" --team-id "$DARWIN_DEV_TEAM" --wait`.

Control flow: receives artifact path as `$1` and blocks until notarization completes.

State/persistence behavior: no repository writes. It sends artifact data and Apple credentials to Apple's notarization service.

Dependencies/integration: macOS release pipeline with `xcrun`, notarytool, and `DARWIN_DEV_*` environment secrets.

Risks: comment warns not to run on multi-user systems because secrets are passed as process arguments. No argument validation or retry behavior.

Test signals: notarytool exit status and notarization logs in CI.
