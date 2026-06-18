# sources/sync-backup/kopia/.github/workflows/stale.yml

## Purpose
Automates stale issue and pull request management. It runs on a Sunday/Wednesday schedule and can be manually dispatched.

## APIs, Control Flow, and Integration Points
The workflow grants `issues: write` and `pull-requests: write`, then invokes pinned `actions/stale`. Configuration processes older items first, caps operations to 100 per run, labels stale issues and PRs with `stale`, exempts issues labeled `bug` or `keep-open`, exempts PRs labeled `keep-open`, and posts close messages explaining how to reopen and remove the stale label.

## State, Persistence, and Dependencies
Persistent state is GitHub issue/PR labels, comments, and closures. There is no code checkout and no artifact state. The behavior depends entirely on the versioned stale action and repository labels.

## Risks and Test Signals
The workflow can close community work without human intervention, so label policy accuracy is important. The absence of explicit stale day settings means defaults from `actions/stale` control timing; future action version changes could affect behavior. This is an operations workflow, not a test signal.
