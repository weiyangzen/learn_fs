# sources/sync-backup/unison/man/unison.1.in

Purpose: mandoc template for the Unison `unison(1)` manual page.

Important content: name/synopsis/description, generated placeholders `@OPTIONS_SHORT@` and `@OPTIONS_FULL@`, root URI grammar, path/pathspec syntax, profiles, termination signals, environment variables, files, examples, exit statuses, compatibility notes, and links to the full manual.

Control flow: no program control flow. Build tooling substitutes option placeholders and emits `man/unison.1`.

State/persistence: documents Unison state locations such as `$UNISON`, `~/.unison/*.prf`, archive files, fingerprint caches, and locks. Also documents command behavior for socket, ssh, file, local roots, continuous sync, and GUI limitations.

Dependencies/integration: integrates with the documentation/manpage generation target and must stay aligned with actual preferences and runtime behavior.

Risks: stale documentation can mislead users about path grammar, environment variables, exit status semantics, and compatibility. The generated option placeholders are critical; if substitution fails the manpage is incomplete.

Test signals: docs CI should generate `man/unison.1`; manual review should compare documented options with `-help`/`-prefsdocs` output and self-test behavior.
