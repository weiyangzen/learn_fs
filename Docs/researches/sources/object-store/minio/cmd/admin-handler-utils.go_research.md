## sources/object-store/minio/cmd/admin-handler-utils.go

Purpose: shared admin-handler helpers for authorization and error mapping. Important APIs are `validateAdminReq`, `AdminError`, `toAdminAPIErr`, `toAdminAPIErrCode`, `exportError`, `importError`, and `importErrorWithAPIErr`.

Control flow in `validateAdminReq` checks object-layer and notification readiness, then tries each requested admin action until one authorizes; access-denied tries the next action while other auth errors are returned immediately as JSON. `toAdminAPIErr` maps policy, config, IAM, KMS, decommission, tier, site-replication, and generic errors into MinIO API error structures and status codes. State is not persisted. Dependencies include auth, policy, config, madmin, KES, object layer globals, and API error tables. Risks include incomplete error classification, action-list authorization ambiguity, and exposing wrapped error details. Tests referenced by function inventory likely exist outside this subset.
