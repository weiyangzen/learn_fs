## sources/object-store/garage/src/api/common/router_macros.rs

Purpose: centralizes repetitive route and query parsing macros for S3/K2V/admin routers.

Important APIs/types/functions: exported macros `router_match!` and `generateQueryParameters!`. `router_match!` supports endpoint variant matching/extraction, legacy path parsers, v2 admin path/body parser generation, generic method/key/keyword parsers, parameter extraction modes, and endpoint `name()`. `generateQueryParameters!` creates `Keyword`, `QueryParameters`, `from_query`, and `nonempty_message`.

Control flow: generated parsers match `(method, path)` or `(keyword, has_key)` and construct endpoint/request variants. Query parameter parsing rejects duplicate known fields and multiple keywords, ignores empty known values, and logs unknown non-AWS/response query parameters.

State/persistence: none.

Dependencies/integration: all routers depend on generated names and parsing conventions. Admin v2 macro also relies on `paste!` and caller imports such as `parse_json_body`, `Error`, `AdminApiRequest`, and request type names.

Risks: macro errors can be hard to debug and affect multiple APIs. Empty query values are ignored by design/FIXME. `@gen_path_parser_v2` assumes route names match request struct names. Unknown query parameters may not fail requests.

Test signals: no local tests; behavior is indirectly compiled and exercised through router tests/integration tests.
