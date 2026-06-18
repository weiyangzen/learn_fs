## sources/sync-backup/restic/internal/repository/doc.go

Purpose: package-level design documentation for repository storage abstractions.

Important concepts: documents `File` as backend-addressed stored data, usually content-addressed by SHA-256 of ciphertext; `Blob` as typed data/tree content identified by plaintext hash; and `Pack` as one or more encrypted blobs plus encrypted header in a backend file.

Control flow and state: no executable code.

Dependencies and integration points: this documentation explains the invariants used by pack, index, checker, crypto, and repository code.

Risks and test signals: documentation must stay aligned with repository format changes, especially around compression and index versions. No tests are attached to this doc file.
