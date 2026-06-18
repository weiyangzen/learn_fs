## sources/user-network-fs/gcsfuse/.github/workflows/stale.yml

Purpose: Closes inactive issues that are waiting on customer input.

Important APIs/types/functions: scheduled daily at 02:30 UTC. Single `close-issues` job grants `issues: write` and runs `actions/stale@v5` with `only-labels: pending customer action`, no stale transition, close after 14 days, no PR stale/close behavior, and a fixed close message.

Control flow: the stale action scans matching issues and closes those with the label after the configured inactivity window.

State and persistence: mutates issue state by closing issues and adding configured close message/label behavior.

Dependencies and integration points: GitHub Actions, default token, and issue triage labels.

Risks: incorrect label application can close valid issues. No PR closing is configured. Older action major version should be monitored.

Test signals: scheduled workflow logs and issue closures after 14 days of inactivity with the target label.
