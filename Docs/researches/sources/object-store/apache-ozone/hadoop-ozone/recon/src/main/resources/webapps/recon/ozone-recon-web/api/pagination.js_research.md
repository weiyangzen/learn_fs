# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/pagination.js

## Purpose

`pagination.js` is a CommonJS json-server middleware used by the Recon web UI development mock API. It simulates backend-style cursor pagination for unhealthy container endpoints after `json-server` has already rewritten public Recon API paths through `api/routes.json`. The file exists because json-server v0.15 applies custom middlewares after its own URL rewriting, so the middleware must match internal mock resource paths such as `/unhealthyMissing` instead of the original `/api/v1/containers/unhealthy/MISSING`.

The behavior is scoped to five unhealthy-container resources: missing, under-replicated, over-replicated, mis-replicated, and replica-mismatch containers. All other requests are passed through to the next json-server handler.

## Important APIs, Types, and Functions

- `fs.readFileSync(DB_PATH, 'utf-8')` loads `api/db.json` synchronously on each matching request.
- `path.join(__dirname, 'db.json')` anchors the mock database path to the API directory.
- `PATH_TO_KEY` maps rewritten request paths to top-level keys in `db.json`.
- `module.exports = function paginationMiddleware(req, res, next)` exports the Express/json-server middleware.
- `req.path` is the post-rewrite json-server resource path.
- `req.query.limit` and `req.query.minContainerId` are parsed as decimal integers.
- `res.json(...)` sends the paginated response and terminates the middleware chain for supported paths.

There are no custom classes or TypeScript types. The effective response shape contains count fields, `firstKey`, `lastKey`, and `containers`.

## Control Flow

The middleware first resolves `dbKey = PATH_TO_KEY[req.path]`. If the path is not one of the five supported unhealthy-container resources, it calls `next()` immediately.

For supported paths it normalizes query values:

- `limit` defaults to `10` and is clamped to at least `1`.
- `minContainerId` defaults to `0` and is clamped to at least `0`.

It then reads and parses `db.json`. If file reading or JSON parsing fails, it logs an error prefixed with `[pagination]` and falls through via `next()`, allowing json-server's normal route handling to respond.

If the selected `dbKey` is missing from the parsed database, the middleware also calls `next()`. Otherwise, it filters `resource.containers` to entries where `containerID > minContainerId`, sorts the remaining rows ascending by `containerID`, slices the first `limit` entries, calculates `firstKey` and `lastKey` from the resulting page, and returns JSON with all unhealthy count fields plus the page.

## State and Persistence Behavior

The middleware is stateless between requests. It intentionally re-reads `db.json` for every matching request, so edits to mock data are visible without restarting json-server. It does not mutate the request, in-memory resource objects, or `db.json`; sorting is applied after `.filter(...)`, so it sorts a new array rather than the database array itself.

Pagination state is caller-owned. Clients pass the previous page's `lastKey` as `minContainerId` to request the next page. Empty pages return `firstKey: 0`, `lastKey: 0`, and an empty `containers` array.

## Dependencies and Integration Points

This middleware depends on Node `fs`/`path`, json-server/Express middleware semantics, `api/db.json`, the unhealthy-container rewrites in `api/routes.json`, and the `mock:api` script in `package.json`. It is the custom layer that makes mocked unhealthy-container list endpoints behave like cursor-paginated Recon backend endpoints.

## Risks

Route changes in `routes.json` can silently bypass pagination unless `PATH_TO_KEY` is updated. The synchronous file read is acceptable for a local mock but unsuitable for production. Invalid numeric query values are silently coerced, `parseInt` accepts partial strings, duplicate or non-numeric `containerID` values can break cursor behavior, and count fields can drift from fixture rows.

## Test Signals

Run `pnpm mock:api` or `pnpm dev` and request each unhealthy endpoint with `limit` and `minContainerId`. Expected signals are ascending `containerID` order, correct `firstKey`/`lastKey`, at most `limit` rows, and pass-through behavior for unrelated routes.
