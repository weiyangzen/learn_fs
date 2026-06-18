# sources/user-network-fs/rclone/backend/doi/link_header_internal_test.go

Purpose: Unit-tests the DOI backend's lightweight `Link` header parser.

Important APIs, types, and functions: `TestParseLinkHeader` compares parsed output with expected `headerLink` values for a linkset header and a multi-link pagination header.

Control flow: The test first verifies whitespace-tolerant parsing of href, `rel`, `type`, and empty extras. It then parses four comma-separated links and asserts the exact ordered slice.

State and persistence behavior: In-memory parsing only, no external state.

Dependencies and integration points: Uses testify assertions. These cases support Invenio endpoint discovery, where linkset headers are preferred over URL guessing.

Risks: Tests do not cover malformed entries, unquoted values, extras, mixed-case keys, or quoted commas/semicolons. The exact-slice assertion documents current order-preserving behavior.

Test signals: Passing tests show basic RFC-style link headers are parsed into the shape expected by `resolveInvenioEndpoint`.
