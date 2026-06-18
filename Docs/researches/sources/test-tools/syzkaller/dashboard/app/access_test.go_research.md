<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/access_test.go -->
# sources/test-tools/syzkaller/dashboard/app/access_test.go research

Purpose: comprehensive tests for dashboard access-level assignment, UI/text visibility, reference leakage, and user authorization logic.

Important APIs, types, and functions: `TestAccessConfig`, `TestAccess`, `makeUser`, and `TestUserAccessLevel`. The test uses `NewSpannerCtx`, dashboard clients, bug/crash/build helpers, AI job creation, `AuthGET`, and App Engine login URL checks.

Control flow: `TestAccess` creates fixtures across `access-admin`, `access-user`, and `access-public` namespaces, uploads builds/crashes with access-specific marker strings, transitions bugs through invalid/fixed/open/dup/reporting states, creates AI jobs, records expected entity access levels, then requests each URL at lower access levels and scans replies for forbidden references. `TestUserAccessLevel` table-tests auth-domain, unauthenticated, ACL-authorized, and admin downgrade behavior.

State and persistence: populates test datastore/Spanner state with builds, bugs, crashes, texts, assets, reportings, and AI jobs. All state is test-scoped through the test context.

Dependencies and integration: validates `access.go` plus many handlers that render pages or serve text. It also exercises dashboard config, reporting updates, crash assets, AI job pages, and App Engine user/login behavior.

Risks: the test is intentionally broad and long; failures can originate in rendering or fixture setup rather than the access function itself. Short mode skips many combinations and mainly checks no public access to non-public URLs.

Test signals: expected HTTP OK/redirect/forbidden outcomes, absence of higher-level marker strings in lower-level responses, correct machine-info namespace behavior, and exact `userAccessLevel` table outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/access_test.go -->
