# sources/object-store/openstack-swift/swift/common/middleware/acl.py

Purpose: formats, parses, normalizes, and evaluates Swift ACL header values, supporting legacy comma-delimited ACLs and JSON version-2 account ACLs.

Important APIs/types/functions: `clean_acl` validates and canonicalizes v1 ACL strings; `format_acl_v1`, `format_acl_v2`, and `format_acl` produce header values; `parse_acl_v1`, `parse_acl_v2`, and `parse_acl` decode them; `referrer_allowed` evaluates referer host rules; `acls_from_account_info` extracts account ACLs from sysmeta.

Control flow: `clean_acl` splits on commas, trims whitespace, preserves plain groups, normalizes referrer aliases to `.r:`, rejects referrers on write ACLs, handles negated hosts and wildcard/domain shorthand, and rejects unknown designators or empty hosts. V1 parse splits referrers from groups and URL-decodes groups. V2 format emits compact ASCII JSON with sorted keys, while V2 parse returns a dict, `{}` for empty string, or `None` for absent/invalid/non-dict input. `referrer_allowed` walks ACL entries in order so later allow/deny matches update the decision. `acls_from_account_info` reads `core-access-control` sysmeta and returns only populated admin/read-write/read-only lists.

State and persistence: stateless parsing logic. ACL persistence occurs elsewhere as headers/sysmeta.

Dependencies and integration: uses JSON and `urllib.parse` for unquoting and host parsing. Used by auth and proxy middleware to interpret account/container ACL headers and referer grants.

Risks: comma and colon parsing is intentionally simple and tied to v1 syntax; referer-based access depends on client-provided headers and should not be treated like authentication; ordering of allow/deny rules is significant; `parse_acl_v2` silently returns `None` for invalid data. Tests should cover messy normalization, invalid designators, write ACL referrer rejection, wildcard/domain/negative referrers, v2 JSON round trips, invalid v2 data, and account ACL extraction.
