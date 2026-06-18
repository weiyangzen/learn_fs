# sources/sync-backup/kopia/internal/feature/feature_test.go

Purpose: verifies feature compatibility filtering and unsupported-feature message composition.

Important APIs/types/functions: `feature.Required`, `feature.Feature`, `feature.GetUnsupportedFeatures`, `Required.UnsupportedMessage`, and `IfNotUnderstood` fields `Message`, `URL`, and `UpgradeToVersion`.

Control flow: `TestFeature` runs table cases for nil inputs, partial support, and full support. `TestFeatureUnsupportedMessage` maps representative `Required` values to exact expected strings.

State/persistence behavior: no persistent state is used. The tests indirectly protect JSON-facing field semantics by exercising zero-value behavior and optional message fragments.

Dependencies/integration: uses `testify/require`. The tests define package `feature_test`, so they exercise only the exported API.

Risks/test signals: message assertions are exact, so intended wording changes require test updates. The tests do not cover `Warn` because warning policy is implemented by callers rather than this package.
