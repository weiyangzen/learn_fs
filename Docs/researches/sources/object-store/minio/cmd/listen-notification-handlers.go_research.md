# sources/object-store/minio/cmd/listen-notification-handlers.go

## Purpose

`listen-notification-handlers.go` implements the S3-compatible event stream endpoint for listening to local and peer object notifications. It authenticates listen requests, validates filters, subscribes to local events, fans in peer events, and streams JSON event records with optional keepalive behavior.

## Important APIs, Control Flow, And State

`ListenNotificationHandler` builds a request context and audit log, verifies the object layer exists, extracts the optional bucket from mux vars, and chooses `policy.ListenNotificationAction` for cluster-wide listening or `policy.ListenBucketNotificationAction` for a bucket. Query parameters `prefix` and `suffix` are validated with `event.ValidateFilterRuleValue`; multiple values produce S3 filter errors. Event names are parsed into `event.Name` values and merged into a `pubsub.Mask`. When a bucket is specified, `GetBucketInfo` ensures it exists.

The handler creates an event rules map with a UUID target, sets event-stream headers, and creates buffered `mergeCh` and `localCh`. A goroutine encodes local events as `{"Records":[...]}` JSON using a reusable grid byte buffer. `globalHTTPListen.Subscribe` filters by bucket and rules map. Peer REST clients receive `Listen` calls with the same query values and feed `mergeCh`. The response loop writes peer/local JSON bytes, flushes when the queue drains, emits empty JSON records on explicit `ping=<seconds>`, or emits a deprecated space keepalive every 500 ms when `ping` is absent.

State is streaming and subscription state tied to request cancellation. Dependencies include MinIO event, grid buffer pool, peer REST clients, pubsub, HTTP flush helpers, mux vars, and policy checks.

## Risks And Test Signals

Risks include slow clients consuming buffer memory, goroutine lifetime if context cancellation is missed, byte-buffer ownership between JSON encoding and write paths, peer fan-in partial failure handling, and deprecated keepalive compatibility. No direct test in this subset covers the handler; likely coverage is integration-level notification tests.
