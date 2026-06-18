# sources/user-network-fs/rclone/backend/doi/link_header.go

Purpose: Provides a small parser for HTTP `Link` headers used to discover Invenio API/linkset endpoints.

Important APIs, types, and functions: `headerLink` stores href, rel, type, and extra attributes. `parseLinkHeader` parses a comma-separated header into links. `parseLink` parses a single link-value. `parseKeyValue` parses `key=value` attributes and removes surrounding double quotes.

Control flow: `parseLinkHeader` splits on commas, trims spaces, delegates to `parseLink`, and drops invalid entries. `parseLink` splits on semicolons, requires the first part to be `<...>`, and maps lowercased `rel` and `type` specially while preserving other keys in `Extras`.

State and persistence behavior: Stateless string parsing only.

Dependencies and integration points: Uses regexp and strings. `resolveInvenioEndpoint` consumes parsed links looking for `rel=linkset` and `type=application/linkset+json`.

Risks: The parser is intentionally lightweight and does not handle commas or semicolons inside quoted attribute values. Regexes are greedy, so unusual angle-bracket content could parse broadly. Attribute key casing for extras is preserved, while rel/type matching is lowercased.

Test signals: `link_header_internal_test.go` covers a single link with quoted attributes and a multi-link pagination-style header.
