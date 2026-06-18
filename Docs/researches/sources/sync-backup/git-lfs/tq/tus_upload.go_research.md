# sources/sync-backup/git-lfs/tq/tus_upload.go

Purpose: resumable upload adapter for the tus.io protocol.

Important APIs/types/functions: `TusAdapterName`, `TusVersion`, `tusUploadAdapter`, `DoTransfer`, and `configureTusAdapter`.

Control flow: gets upload action, sends `HEAD` with `Tus-Resumable`, parses `Upload-Offset`, skips if already complete, opens file, emits progress for resumed bytes, sends `PATCH` from offset with tus headers and callback body, maps network/403 errors to retriable, validates status, drains response, and verifies upload.

State and persistence: reads local object file and relies on server-side resumable upload offset; no local persistence beyond progress state.

Dependencies and integration points: registered only when `lfs.tustransfers` config permits; uses basic upload's start callback reader and verify flow.

Risks: does not validate response `Upload-Offset` after PATCH despite comment saying it should. Offset seek uses `io.SeekCurrent` in the start callback after client rewinds; this depends on body rewind behavior. Unsupported/malformed headers fail non-retriably.

Test signals: no direct tus tests in this subset.
