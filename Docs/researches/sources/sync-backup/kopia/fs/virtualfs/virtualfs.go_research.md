## sources/sync-backup/kopia/fs/virtualfs/virtualfs.go

Purpose: implements in-memory `fs.Entry`, static directories, one-shot streaming directories, and one-shot streaming files.

Important APIs/types/functions: `NewStaticDirectory`, `NewStreamingDirectory`, `StreamingFileFromReader`, `StreamingFileWithModTimeFromReader`, `virtualEntry`, `staticDirectory`, `streamingDirectory`, `virtualFile`, and errors for reused readers/iterators.

Control flow, state, and persistence: static directories copy their entry slice for iteration and support repeated traversal. Streaming directories guard a single iterator with a mutex and consume it on first `Iterate`. Streaming files return their reader once and set it nil afterward. There is no persistence beyond in-memory entries and reader state.

Dependencies and integration points: supplies synthetic trees to components expecting `fs.Directory` or `fs.StreamingFile`, useful for generated content and tests.

Risks and test signals: risks are accidental multiple reads and data races on `virtualFile.GetReader`, which explicitly delegates concurrency safety to callers. Tests cover static lookup, streaming one-shot behavior, callback error propagation, and mod-time injection.
