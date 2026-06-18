# sources/object-store/minio/cmd/logging.go

## Purpose

`logging.go` centralizes category-specific logging wrappers for MinIO subsystems. It gives call sites short, named helpers that route errors and events to `internal/logger` with stable subsystem tags.

## Important APIs, Control Flow, And State

Most functions are one-line wrappers around `logger.LogIf`, `logger.LogOnceIf`, `logger.LogAlwaysIf`, `logger.LogOnceConsoleIf`, or `logger.Event`. Categories include proxy, replication, IAM, rebalance, admin, authN, authZ, peers, internal/bug, healing, batch, bootstrap, DNS, transition, config, scanner, ILM, encryption, storage, decommission, etcd, metrics, S3, SFTP, shutdown, STS, tier, and KMS. `iamLogIf`, `peersLogIf`, `peersLogAlwaysIf`, and `peersLogOnceIf` suppress `grid.ErrDisconnected` to avoid noisy logs during expected peer disconnects. `KMSLogger` implements a small logger interface with `LogOnceIf` and `LogIf` methods for the KMS module.

The file has no persistent state. It depends on `context`, `errors`, `internal/grid`, and `internal/logger`.

## Risks And Test Signals

The value is consistency, but risks include category typos becoming observability contract changes, unexpected suppression of `grid.ErrDisconnected`, and wrapper proliferation hiding severity choices. There are no direct tests in this subset. Coverage is indirect through subsystem tests and runtime logging behavior.
