# sources/sync-backup/casync/test/test-caencoder.c

Purpose: end-to-end smoke test for archive encoder and decoder streaming APIs.

Important APIs/types/functions: `encode` drives `CaEncoder` steps, writes emitted archive bytes to a temp file, logs file transitions, and validates archive offset against fd position. `decode` drives `CaDecoder`, feeds bytes on request, and logs decoded file transitions.

Control flow/state: creates a temp archive under `/var/tmp`-style directory, encodes a base directory (argv or `.`), reopens the archive, decodes it, and unlinks the temp file.

Dependencies/integration: exercises caencoder/cadecoder/caformat, feature flags, base fd handling, temp utilities, and low-level I/O.

Risks/test signals: it validates streaming state machines but does not compare reconstructed filesystem output. Failures surface as negative errno or assertion failures during state transitions.

Source research group: `subset-b-009122`.
