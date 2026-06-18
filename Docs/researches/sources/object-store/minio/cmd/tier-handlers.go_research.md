# sources/object-store/minio/cmd/tier-handlers.go

Purpose: admin HTTP handlers for managing remote transition tiers. These endpoints let authorized admins add, list, edit, remove, verify, and inspect stats for tier backends used by ILM/object transition.

Important APIs and functions: `AddTierHandler`, `ListTierHandler`, `EditTierHandler`, `RemoveTierHandler`, `VerifyTierHandler`, and `TierStatsHandler` are methods on `adminAPIHandlers`. Admin errors defined here include tier already exists/not found, non-uppercase names, missing bucket, invalid credentials, and reserved name. Handlers authorize with `validateAdminReq` using `policy.SetTierAction` or `policy.ListTierAction`.

Control flow: add/edit decrypt the encrypted admin request body with the caller's secret key, unmarshal JSON into `madmin.TierConfig` or `madmin.TierCreds`, reload disk config to catch missed peer updates, mutate `globalTierConfigMgr`, save the config, then broadcast `LoadTransitionTierConfig`. Add rejects reserved storage class names (`STANDARD`, `RRS`) and supports a `force` query to ignore in-use backend checks. Remove reloads config, parses `force=true`, removes from the manager, saves, and notifies peers. Verify delegates to `TierConfigMgr.Verify`. Stats loads data usage, merges last-day stats from `globalNotificationSys`, marshals `madmin.TierInfo`, and returns JSON.

State and persistence: handlers persist tier config through `TierConfigMgr.Save` into the MinIO metadata bucket. List returns `X-MinIO-TierCfg-RefreshedAt` so clients can see refresh age. Mutating handlers update in-memory and persisted state and ask peer nodes to reload transition tier config.

Dependencies and integration points: depends on `madmin-go` request/response types and request encryption, `jsoniter`, MinIO admin auth/error plumbing, lifecycle storage-class constants, mux path variables, global data-usage loading, and notification system tier stats.

Risks: stale config across distributed nodes is mitigated by reload-before-write and peer notification, but concurrent edits can still race at the object-store persistence boundary. Decrypting with the admin credential secret means body handling must remain aligned with madmin clients. Reserved-name validation prevents ambiguity with internal storage classes.

Test signals: this file is exercised indirectly by admin API and tier manager tests. Useful coverage would verify encrypted body failures, unauthorized policies, reserved names, force semantics, reload/save failures, peer notification, and stats JSON with daily bins.
