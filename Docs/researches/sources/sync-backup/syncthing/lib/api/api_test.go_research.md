# sources/sync-backup/syncthing/lib/api/api_test.go

Purpose: Broad integration and unit test coverage for the API service, static assets, authentication, CSRF, headers, event subscriptions, browsing, certificate policy, config modifications, and hostname sanitization.

Important APIs/types/functions: Defines shared test config, `startHTTP`, request helpers, session-cookie helpers, `httpTestCase`, and many `Test...` functions. It uses mocks for model, events, discovery, connections, and folder summaries.

Control flow: `startHTTP` constructs a `service`, starts it under suture, waits for a random localhost listener address, and returns a base URL. Endpoint tests send real HTTP requests with API keys or auth cookies. Config tests use a live config wrapper and verify PUT/PATCH/DELETE behavior through REST routes.

State and persistence behavior: Tests use temporary sqlite misc DBs, temp config files, testdata config base directory, and temporary fake filesystems. Cleanup cancels supervisors and closes DBs.

Dependencies and integration points: Exercises `api.go`, `api_auth.go`, `api_csrf.go`, `api_statics.go`, `confighandler.go`, `tokenmanager.go`, `assets`, config wrappers, and mocks generated in other packages.

Risks: Because many tests run in parallel and use actual listeners, timeouts and port/listener behavior can be environment-sensitive. Several tests rely on noauth paths returning 200 even when unauthenticated, which encodes middleware order.

Test signals: Very strong signal for public REST compatibility: expected status codes/content types, auth success/failure, cookie lifecycle, CSRF, host checking including IPv6/container skip, CORS/OPTIONS, event mask parsing, browse sorting and prefix matching, certificate regeneration, config changes, and sanitized hostnames.
