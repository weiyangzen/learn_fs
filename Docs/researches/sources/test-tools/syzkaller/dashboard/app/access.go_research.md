<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/access.go -->
# sources/test-tools/syzkaller/dashboard/app/access.go research

Purpose: dashboard authorization and text-asset access control for public, user, and admin visibility levels.

Important APIs, types, and functions: defines `AccessLevel`, `AccessPublic`, `AccessUser`, `AccessAdmin`, `ErrAccess`, `checkAccessLevel`, `isEmailAuthorized`, `currentUser`, `accessLevel`, `userAccessLevel`, `checkTextAccess`, `checkCrashTextAccess`, `checkJobTextAccess`, `Bug.sanitizeAccess`, and `sanitizeReporting`.

Control flow: request access is determined from App Engine user identity or OAuth, trusted auth domain, admin status, ACL entries, and optional `access` downgrade query. Text access dispatches by text tag: job-owned texts query `Job`, crash-owned texts query `Crash` and parent `Bug`, some deduplicated namespace texts are allowed by namespace, and unknown/default text requires admin. Bug access is sanitized by current reporting stage, with fixed/invalid/committed bugs optionally visible at later reporting levels after private reporting fields are stripped.

State and persistence: reads global config, App Engine user context, datastore `Crash`, `Job`, and `Bug` entities. It mutates in-memory bug reporting fields during sanitization but does not persist those sanitized copies.

Dependencies and integration: uses App Engine datastore, logging, user/OAuth APIs, dashboard text tag constants, namespace reporting config, and page/API handlers that call `checkAccessLevel` or `checkTextAccess`.

Risks: access decisions depend on accurate datastore reverse links from text IDs to jobs/crashes. Deduplicated machine/kernel-config style texts rely on namespace checks because exact ownership is not always recoverable. `trustedAuthDomain` is mutable for tests and must remain production-safe.

Test signals: access tests cover config levels, signed-in versus public redirects, forbidden statuses, text URLs by numeric/hex IDs, sanitized hidden references, admin downgrades, ACL email/domain matching, and OAuth/public fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/access.go -->
