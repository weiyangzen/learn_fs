## sources/sync-backup/bup/test/ext/test-get-repair-bupm

Purpose: tests repair of abridged `.bupm` metadata caused by older Bup bugs.

Important control flow: creates two saves, then replaces the newer save’s `.bupm` with the older shorter one. It validates refs detect the abridged metadata, verifies normal rewrite rejects it, then runs `bup get --repair`, captures the repair ID, checks commit trailers for version/argv/repair/save/lost-meta entries, restores the repaired save, and inspects restrictive metadata with `bup xstat`.

State and dependencies: direct Git tree and branch manipulation. Depends on `validate-refs --bupm`, `rewrite.py` repair mode, trailer generation, restore, and xstat.

Risks covered: metadata loss must be explicit in trailers and repaired files must restore with restrictive safe defaults, not guessed original metadata.
