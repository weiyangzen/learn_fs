# sources/sync-backup/rsync/.github/workflows/fleettest.yml

Purpose: CI sanity test for rsync's fleettest orchestration script.

Important APIs/types/functions: prepares local SSH to localhost, writes a two-target JSON fleet configuration, runs `testsuite/fleettest.py --list`, then runs fleettest timing against two local targets.

Control flow: creates SSH key, trusts localhost host keys, starts sshd, verifies batch-mode SSH, then exercises parallel target isolation using two build directories.

State and persistence: temporary local SSH config and fleet JSON in the runner; no durable artifacts indicated.

Dependencies/integration: depends on OpenSSH service availability and Python fleettest tooling.

Risks: localhost SSH setup can be runner-sensitive; failures may reflect environment rather than rsync code.

Test signals: list sanity and successful parallel local fleet runs.
