# sources/sync-backup/git-lfs/tq/verify.go

Purpose: optional post-upload verification request handling.

Important APIs/types/functions: `maxVerifiesConfigKey`, `defaultMaxVerifyAttempts`, and `verifyUpload`.

Control flow: obtains `verify` action if present, builds POST JSON with oid/size, sets Git LFS JSON headers and action headers, clamps configured attempts to at least default, logs request, and retries `Do`/`DoWithAuth` until a request succeeds or attempts are exhausted.

State and persistence: no durable state; consumes response bodies by closing them.

Dependencies and integration points: called by basic, tus, custom, and SSH upload paths after upload completion. Depends on `lfsapi.Client` and action auth metadata.

Risks: successful HTTP response status is not checked, only transport error/close. `t.Oid[:7]` in tracing assumes OID length at least seven. Config uses `max(default, configured)`, so values below 3 cannot reduce attempts.

Test signals: `verify_test.go` covers no-action success and successful POST with headers/auth access mode.
