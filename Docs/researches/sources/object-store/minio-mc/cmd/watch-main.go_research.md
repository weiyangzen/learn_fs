## sources/object-store/minio-mc/cmd/watch-main.go

Purpose: implements `mc watch`, a CLI for streaming object notification events from S3-compatible targets or local paths. Important surfaces are `watchCmd`, `watchFlags`, `watchMessage`, `checkWatchSyntax`, and `mainWatch`.

Control flow validates one target, parses event/prefix/suffix/recursive filters, creates a client, calls `Client.Watch`, and starts a goroutine that selects over global cancellation, event batches, and errors. Each event is converted to `watchMessage` for JSON or colored text. State is streaming only; no persistence. Dependencies include minio notification types, `probe`, humanized sizes, console colors, and global context. Risks include long-running goroutine lifecycle, closing `DoneChan` on cancellation, and event filter semantics delegated to client implementations. Functional test script covers `test_watch_object` only outside Mint mode.
