## sources/object-store/garage/src/api/k2v/api_server.rs

Purpose: wires the K2V API into the shared generic server, including route parsing, SigV4 auth, bucket permission checks, CORS, and endpoint dispatch.

Important APIs/types/functions: `K2VApiServer`, `K2VApiEndpoint`, `K2VApiServer::run`, `ApiHandler for K2VApiServer`, and `ApiEndpoint for K2VApiEndpoint`.

Control flow: `parse_endpoint` delegates to `Endpoint::from_request`. `handle` processes `OPTIONS` before auth, then verifies SigV4 with service `k2v`, resolves the bucket against the access key, checks read/write/owner permissions from endpoint authorization type, looks up applicable CORS for GET/HEAD/POST, builds `ReqCtx`, dispatches to item/index/batch/range handlers, and adds CORS headers to successful responses. `key_id_from_request` parses Authorization headers for access logging.

State/persistence: reads Garage bucket/key state and delegates mutations to K2V RPC handlers. No local persistence.

Dependencies/integration: integrates `garage_api_common::{generic_server,cors,helpers,signature}`, K2V handler modules, and Garage model.

Risks: only GET/HEAD/POST success responses receive CORS decoration; other methods should be preflighted. OPTIONS is unauthenticated and uses bucket-name parsing. Permission mapping in router is security-critical.

Test signals: no local tests; should be covered by K2V API integration tests for auth, CORS, and dispatch.
