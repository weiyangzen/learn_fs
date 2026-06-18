<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest.go -->
# sources/sync-backup/restic/internal/backend/rest/rest.go

## Purpose
Implements the REST protocol backend over HTTP.

## Important APIs, Types, And Functions
Backend, restError, NewFactory, Open, Create, Save, Load/openReader, Stat, Remove, List/listv1/listv2, Delete, Close, Warmup/WarmupWait, and content type constants are central.

## Control Flow
Open normalizes layout URL and installs an http.Client. Create checks config absence then POSTs ?create=true. Save POSTs object bytes with ContentLength and rewindable GetBody. Load issues Range GETs and drains/EOF-checks bodies. List GETs a type directory and decodes v1 names with per-file HEADs or v2 name/size JSON.

## State And Persistence Behavior
Repository state is remote on a REST server. Local state is URL, connection count, client, and layout.

## Dependencies And Integration Points
Depends on net/http/url/json, backend/layout/location/util, debug/errors/feature, and the configured RoundTripper.

## Risks And Edge Cases
Risks include HTTP status classification, body drain requirements for connection reuse, rclone-specific 404 handling, range/content-length mismatch under BackendErrorRedesign, and retryability decisions.

## Test Signals
REST unit and integration tests cover list protocols, rest-server execution, unix sockets, and generic backend behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest.go -->
