<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/event-notification.go -->
# sources/object-store/minio/cmd/event-notification.go

## Purpose
Implements the bucket event notification dispatcher that maps bucket notification rules to target IDs, builds S3-compatible event payloads, and sends events to configured targets and HTTP listeners.

## Important APIs, types, and functions
- `EventNotifier` owns an `event.TargetList` and bucket-to-`event.RulesMap` map under an RW mutex.
- `NewEventNotifier`, `GetARNList`, `InitBucketTargets`, `AddRulesMap`, `RemoveNotification`, `RemoveAllBucketTargets`, `Targets`, and `Send` manage notifier state and dispatch.
- `eventArgs` captures event name, bucket, object info, request/response data, host, and user agent.
- `eventArgs.ToEvent` builds the `event.Event` object.
- `sendEvent` strips sensitive metadata, publishes listener events, and invokes `globalEventNotifier`.

## Control flow
Bucket metadata loads notification configs through `set`, validates against registered targets, and stores a rules map. On an object event, `sendEvent` ignores source-replication requests, normalizes actual size, removes encryption/internal metadata, publishes unescaped events to subscribed HTTP listeners, and asks `EventNotifier.Send` to match bucket/object rules and send an escaped event to targets. Target sending can be synchronous based on API config.

## State and persistence behavior
Notification rules are runtime maps derived from persisted bucket metadata. Target definitions come from global notification target configuration. Events include request IDs, node IDs, origin endpoint, deployment ID, object version/ETag/size/content type/user metadata, and sequencer derived from object mod time or current time.

## Dependencies and integration points
Integrates bucket metadata, `internal/event`, target lists, global site region, global API sync-events config, global HTTP listener pubsub, encryption metadata scrubbing, object info sizing, and policy ARN formatting.

## Risks and edge cases
Rule map updates must clone input to avoid caller mutation. Sensitive metadata scrubbing is critical before publishing. Remove events intentionally omit object ETag/size/user metadata. `GetARNList` hides `httpclient+` listener targets. `ToEvent` assumes response element keys exist and falls back to first API endpoint when `globalMinioEndpoint` is empty.

## Test signals
No direct tests here. Signals normally include bucket notification integration tests, ListenNotification subscribers, target delivery behavior, source-replication suppression, and validation errors for missing ARNs.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/event-notification.go -->
