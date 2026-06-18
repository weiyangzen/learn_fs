## sources/object-store/garage/src/api/common/helpers.rs

Purpose: shared request parsing, response body, authorization classification, and utility helpers for bucket APIs.

Important APIs/types/functions: `Authorization`, `ReqCtx`, `host_to_bucket`, `authority_to_host`, `parse_bucket_key`, `key_after_prefix`, body aliases (`EmptyBody`, `ErrorBody`, `BoxBody`), `string_body`, `bytes_body`, `empty_body`, `error_body`, `parse_json_body`, `json_ok_response`, `body_stream`, `is_default`, and `CustomApiErrorBody`.

Control flow: host parsing handles root domains and IPv6 authorities; bucket/key parsing supports virtual-hosted and path-style access; `key_after_prefix` computes exclusive upper bounds for prefix scans; body helpers box hyper bodies, collect JSON, and map streaming frames into data bytes.

State/persistence: `ReqCtx` carries per-request Garage, bucket, params, and API key state to handlers, but helpers do not mutate state.

Dependencies/integration: used by S3/K2V/admin handlers, range scans, CORS, generic error bodies, and route compatibility parsing.

Risks: `parse_json_body` collects whole body in memory. `body_stream` rejects non-data frames. `authority_to_host` must handle IPv6 correctly. Prefix upper-bound logic is subtle around maximum Unicode scalar values.

Test signals: local tests cover bucket/key parsing, virtual-host parsing, authority host extraction with IPv6/ports, root-domain bucket extraction, and prefix successor edge cases.
