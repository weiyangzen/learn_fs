## sources/object-store/minio-mc/cmd/watch.go

Purpose: reusable watch fan-in primitives independent of CLI formatting. It defines `EventInfo`, `WatchOptions`, `WatchObject`, and `Watcher`.

Control flow exposes event/error channels on `WatchObject`; `NewWatcher` creates aggregate channels and a wait group; `Join` calls `client.Watch` with put/delete/bucket creation/removal events, appends the watch object, and starts a goroutine to forward child events/errors into aggregate channels until `DoneChan` closes. `Stop` closes every child `DoneChan` and waits. State is in-memory channel and goroutine coordination. Dependencies are `Client`, `probe`, context, sync, time, and notification event types. Risks include sending to unbuffered aggregate channels without a receiver and close ordering if multiple stop paths close the same child channel. Tests are indirect.
