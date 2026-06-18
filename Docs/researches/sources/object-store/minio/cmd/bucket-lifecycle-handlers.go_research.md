# Research: sources/object-store/minio/cmd/bucket-lifecycle-handlers.go

Purpose: implements S3 bucket lifecycle configuration handlers for PUT, GET, and DELETE. It validates request authentication, parses lifecycle XML, checks object-lock constraints, validates transition tiers, updates bucket metadata, and returns S3-compatible XML or empty success responses.

Important APIs and functions: `bucketLifecycleConfig` names the persisted config as `lifecycle.xml`. `PutBucketLifecycleHandler` requires Content-MD5, authorizes `policy.PutBucketLifecycleAction`, reads object-lock config via `globalBucketObjectLockSys.Get`, parses with `lifecycle.ParseLifecycleConfigWithID`, validates rules with `Validate`, validates tiers with `validateTransitionTier`, tracks expiry-rule changes, marshals XML, and persists through `globalBucketMetadataSys.Update`. `GetBucketLifecycleHandler` authorizes `policy.GetBucketLifecycleAction`, optionally parses `withUpdatedAt`, fetches metadata with `GetLifecycleConfig`, clears internal `ExpiryUpdatedAt`, and writes XML plus optional `x-minio-lifecycle-cfg-updated-at` header. `DeleteBucketLifecycleHandler` authorizes with put-lifecycle action and calls `globalBucketMetadataSys.Delete`.

Control flow: all handlers create request context, audit log on return, verify object API initialization, extract `bucket` via mux vars, authenticate, validate bucket existence, then interact with metadata. PUT compares prior lifecycle rules from disk against new rules to detect removal of expiration behavior; if new config has expiry or an expiry rule was removed, it updates `ExpiryUpdatedAt` before saving.

State and persistence behavior: lifecycle XML is stored inside bucket metadata under the lifecycle slot, with updated timestamps managed by `BucketMetadataSys`. DELETE has special behavior in the metadata layer: removing lifecycle config may persist an empty lifecycle document containing only `ExpiryUpdatedAt` to signal scanner behavior after expiry rules are removed.

Dependencies and integration points: integrates S3 auth policy, mux routing, lifecycle parser/validator, object lock retention config, tier config validation, global bucket metadata, audit logging, and MinIO lifecycle updated-at response headers.

Risks: PUT depends on reading the prior config from disk, so metadata read failures block updates even if in-memory config exists. Expiry-rule removal detection matches by rule ID and could miss semantic changes if IDs are reused incorrectly. GET exposes updated-at only for a MinIO-specific query parameter and returns errors for invalid boolean parsing.

Test signals: `bucket-lifecycle-handlers_test.go` validates wrong credentials, malformed filters/dates, successful PUT/GET/DELETE order, and no-config GET after delete. Tests do not cover `withUpdatedAt`, Content-MD5 failure, transition tier success, or expiry-rule removal timestamp behavior.
