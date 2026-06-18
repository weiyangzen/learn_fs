## sources/sync-backup/syncthing/lib/discover/doc.go

Purpose: Package documentation for local and global Syncthing device discovery protocols.

Important APIs/types/functions: No code APIs; documents announcement JSON, direct/relay address semantics, certificate-authenticated identity, response status codes, reannounce/retry headers, GET lookup query format, and rate-limit behavior.

Control flow: Describes protocol flows for HTTPS POST announcements and HTTPS GET queries.

State and persistence: Documentation only; describes server-side registry behavior conceptually.

Dependencies and integration points: Serves as the protocol reference for `global.go` and `local.go` implementations.

Risks: Documentation can drift from implementation or protocol server behavior.

Test signals: No executable tests.
