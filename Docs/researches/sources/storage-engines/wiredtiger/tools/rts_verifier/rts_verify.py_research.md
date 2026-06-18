# sources/storage-engines/wiredtiger/tools/rts_verifier/rts_verify.py

Purpose: command-line entry point for verifying rollback-to-stable verbose logs.

Important APIs and control flow: parses a single positional log file argument, constructs a `Checker`, reads the file line by line, and for each line containing `WT_VERB_RTS` creates an `Operation` and applies it to the checker.

State and persistence behavior: read-only over the input log. Checker state accumulates in memory for the duration of the process. No output is emitted on success.

Dependencies and integration points: depends on sibling modules `checker` and `operation`. It is intended for logs generated with WiredTiger RTS verbose logging enabled.

Risks: there is no summary output, no count of processed lines, and no controlled error reporting around parser/checker exceptions. Because `checker.py` mostly suppresses assertions, a zero exit code currently means parse success more than semantic correctness.

Test signals: no direct tests. A useful smoke test is running it against a fixture log containing at least one line for each supported RTS operation and confirming nonzero behavior on malformed text.
