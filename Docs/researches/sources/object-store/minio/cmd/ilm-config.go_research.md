# sources/object-store/minio/cmd/ilm-config.go

## Purpose

`ilm-config.go` provides a small concurrency-safe holder for ILM worker configuration. It controls the number of lifecycle expiration and transition workers used elsewhere in the server.

## Important APIs, Types, And Control Flow

`globalILMConfig` is initialized with `ilm.Config{ExpirationWorkers: 100, TransitionWorkers: 100}`. `ilmConfig` wraps the config with an `RWMutex`. `getExpirationWorkers` and `getTransitionWorkers` take read locks and return the current worker counts. `update` takes a write lock and replaces the entire `ilm.Config`.

## State, Dependencies, Integration, Risks, And Tests

State is process-local global config and is not persisted in this file; persistence and parsing belong to the broader config subsystem. The only external dependency is `internal/config/ilm`. Integration points are lifecycle expiration/transition schedulers and config reload paths that call `update`. Risks are invalid worker counts if upstream config validation is bypassed, global defaults that may be too high or low for resource-constrained deployments, and whole-struct replacement losing future fields if update callers pass partial configs. No direct tests are present in this subset.
