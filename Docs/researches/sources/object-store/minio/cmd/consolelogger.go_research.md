# sources/object-store/minio/cmd/consolelogger.go

## Purpose
`consolelogger.go` implements an HTTP-accessible console logger target that writes to the normal console sink, buffers recent log messages, publishes live logs to subscribers, and exposes target statistics.

## Important APIs, Types, And Functions
`HTTPConsoleLoggerSys` holds counters, a pubsub bus, console target, node name, and a ring buffer of `defaultLogBufferCount` entries. `NewConsoleLogger` constructs it. `SetNodeName`, `HasLogListeners`, `Subscribe`, `Content`, `Stats`, and `Send` provide the main behavior. It also implements target compatibility methods `Init`, `Endpoint`, `String`, `Cancel`, `Type`, and `IsOnline`.

## Control Flow
When a subscriber arrives and no listeners exist, `Subscribe` adds the logger as a system target. It snapshots up to `last` matching buffered messages under read lock, emits them in order, then registers the live pubsub subscription. `Send` converts `log.Entry` or string entries into `log.Info`, increments counters, publishes to pubsub, appends to the ring, forwards to the console target, and records failures.

## State And Persistence Behavior
State is in memory only: atomic counters, ring buffer, pubsub subscribers, and current node name. No logs are persisted by this file.

## Dependencies And Integration Points
It integrates with MinIO logger targets, madmin log masks, console target output, generic pubsub, distributed-node naming, and admin log streaming/content APIs.

## Risks And Test Signals
Risks include dropped live logs when subscriber channels block, bounded history overwriting older messages, and the `nodeName` parameter to `SetNodeName` being ignored in favor of `globalLocalNodeName` in distributed mode. No direct tests are in this subset; behavior is typically covered by admin log stream integration tests.
