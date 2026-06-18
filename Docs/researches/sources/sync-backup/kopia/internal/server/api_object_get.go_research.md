# sources/sync-backup/kopia/internal/server/api_object_get.go

Purpose: streams repository object contents over the HTTP API.

Important APIs/types/functions: `handleObjectGet`.

Control flow: parses object ID from the route, checks repository availability and authorization through the request wrapper, opens the object through repository/object APIs, and writes bytes directly to the HTTP response rather than returning JSON.

State and persistence behavior: read-only repository access; no server state mutation.

Dependencies and integration points: registered for `/api/v1/objects/{objectID}` and used by UI restore/browse operations.

Risks and test signals: object ID parsing and streaming errors must not produce partial misleading responses. Tests should cover missing objects, invalid IDs, and large object streaming.
