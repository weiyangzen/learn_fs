## sources/sync-backup/bup/test/ext/test-get-missing

Purpose: verifies `bup get` behavior when source trees are incomplete.

Important control flow: saves two similar directories, prechecks a complete get, removes each directory’s `.bupm` object with `perforate-repo`, then tests failure without ignore, failure when ignore is overridden, skip-and-status behavior with `--ignore-missing --unnamed`, and ordering when multiple gets use different ignore contexts.

State and dependencies: mutates object storage by dropping oids. Depends on `bup get`, `bup join`, Git tree lookup, and stderr matching.

Risks covered: missing source objects must not be silently copied except in the limited unnamed ignore-missing mode, and contextual ignore settings must not leak across later operations.
