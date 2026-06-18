# Research: sources/object-store/minio/cmd/bucket-notification-handlers.go

Purpose: implements S3 bucket notification configuration GET and PUT handlers. It loads/stores notification XML in bucket metadata and synchronizes runtime event notifier rules.

Important APIs and functions: `bucketNotificationConfig` names the config as `notification.xml`. `GetBucketNotificationHandler` authorizes `policy.GetBucketNotificationAction`, verifies bucket existence, loads `globalBucketMetadataSys.GetNotificationConfig`, sets region, validates against `globalEventNotifier.targetList`, prunes stale ARN entries for `event.ErrARNNotFound`, marshals XML, and writes it. `PutBucketNotificationHandler` authorizes `policy.PutBucketNotificationAction`, requires positive Content-Length, parses with `event.ParseConfig` using site region and target list, stores XML via `globalBucketMetadataSys.Update`, converts config to rules, and calls `globalEventNotifier.AddRulesMap`.

Control flow: both handlers follow the standard MinIO handler pattern: context, audit defer, object API nil check, mux bucket extraction, auth, bucket existence, parse/load, validate, persist/respond. GET has compatibility cleanup for stale ARNs that older versions may have accepted; non-ARN validation errors are returned.

State and persistence behavior: notification XML is persisted inside `BucketMetadata`. PUT also updates in-memory notifier rules immediately. GET may remove stale queue entries from the response object but does not persist that cleanup in this handler.

Dependencies and integration points: integrates event config parsing/validation, global site region, event notifier target list/rules map, bucket metadata system, S3 auth policy, XML marshalling, mux, and audit logging.

Risks: GET's stale ARN pruning mutates the config object returned from metadata; because metadata getters return shallow copies with referenced parsed config pointers, this can have in-memory side effects. PUT rejects missing content length and maps non-event parse errors to malformed XML, so diagnostics depend on `event.IsEventError`.

Test signals: no direct tests in this subset. Behavior is likely covered elsewhere by notification handler tests, but this work item provides no local coverage for stale ARN pruning, target validation, or rules-map updates.
