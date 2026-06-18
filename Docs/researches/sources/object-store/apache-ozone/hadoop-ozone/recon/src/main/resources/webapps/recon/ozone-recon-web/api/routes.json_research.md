# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/routes.json

## Purpose

`routes.json` is the json-server route rewrite table for the Recon web UI mock API. It maps public Recon REST paths, including query-specific variants, onto top-level collections in `api/db.json`. This allows the Vite/React UI to call production-looking `/api/v1/...` endpoints while local development serves deterministic fixture data from json-server.

The file covers unhealthy containers, namespace usage and metadata, quota, task status, volumes, buckets, heatmaps, feature flags, open/delete-pending keys, container mismatch reports, datanode decommission/remove endpoints, storage distribution, and pending deletion endpoints.

## Important APIs, Types, and Route Groups

The file is pure JSON consumed by json-server's `--routes` option. Important groups include unhealthy-container rewrites, the generic `/api/v1/*` prefix stripper, namespace usage and summary routes, quota and metadata routes, task/volume/bucket resources, heatmap variants, feature flags, open and delete-pending key resources, OM/SCM mismatch routes, datanode decommission/removal resources, storage distribution, and component-specific pending deletion resources.

There are no executable functions, but json-server pattern syntax provides wildcard and parameter behavior through entries such as `*`, `:id`, and `$1`.

## Control Flow

json-server evaluates route rewrites before the `pagination.js` middleware listed in `package.json`. More specific rules at the top handle unhealthy-container endpoints before the generic `/api/v1/*` prefix stripper. After rewriting, json-server serves the target collection from `db.json`; for unhealthy-container rewritten paths, `pagination.js` intercepts and returns a custom paginated response instead.

The ordering matters because many patterns include query strings. Namespace, heatmap, mismatch, open-key, and delete-pending-key routes distinguish behavior by exact path and query combinations.

## State and Persistence Behavior

The route table stores no runtime state. It defines a deterministic mapping between incoming mock API requests and json-server resource names. Persistent fixture state lives in `api/db.json`, and json-server's `--watch` mode reloads that file during local development.

## Dependencies and Integration Points

This file integrates with the `mock:api` script in `package.json`, `pagination.js`, `api/db.json`, the React frontend API client code, and Playwright/development workflows that run the UI against local mock data. Every rewrite target must match a top-level fixture key in `db.json`.

## Risks

Route matching is brittle where query strings are encoded as full keys. Parameter order, spelling, case, or optional query normalization can miss fixtures. The generic `/api/v1/*` rewrite can hide missing specific routes by rewriting to unexpected resources. The unhealthy-container entries are tightly coupled to `pagination.js`, and inconsistent names such as `keysdeletePendingSummary`, `keydeletePending`, and `dirdeletePending` must remain aligned with `db.json`.

## Test Signals

Run json-server through `pnpm mock:api` and exercise representative URLs: unhealthy container routes with pagination queries, namespace root/volume/bucket/dir/key usage routes, heatmap variants, OM/SCM mismatch routes, and open/delete-pending key routes. UI smoke testing via `pnpm dev` should show no network 404s for mocked Recon endpoints.
