## sources/user-network-fs/gcsfuse/.github/workflows/scorecard.yml

Purpose: Runs OpenSSF Scorecard and uploads SARIF for supply-chain security visibility.

Important APIs/types/functions: triggers on branch protection rule changes, manual dispatch, weekly Monday cron, and pushes to `master`. Uses default `permissions: read-all`; job adds `security-events: write` and `id-token: write`; steps checkout without persisted credentials, run `ossf/scorecard-action@v2.3.3`, upload SARIF artifact, and upload SARIF to code scanning.

Control flow: produce `results.sarif`, publish Scorecard results, retain artifact for five days, and upload to GitHub code scanning.

State and persistence: persists external Scorecard publication, a short-lived Actions artifact, and code-scanning alerts/results.

Dependencies and integration points: requires `secrets.SCORECARD_TOKEN`, OpenSSF Scorecard, upload-artifact, and CodeQL SARIF upload action.

Risks: missing/invalid token may reduce publication or fail the analysis. Action versions are pinned but should be updated for security fixes. Schedule covers only weekly analysis between master pushes.

Test signals: Scorecard workflow check, `results.sarif` artifact, and GitHub code scanning entries.
