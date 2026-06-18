# File Research: sources/virtualization/libguestfs/lib/match.c

PCRE2 wrapper helpers for internal regular-expression matching.

Important behavior:
- Provides boolean matching and capture-returning helpers for one, two, three, four, and six captures.
- Uses `pcre2_match_data_create_from_pattern` with cleanup attributes.
- Treats no-match as normal false/NULL.
- Unexpected PCRE2 errors are logged via debug and treated as no match.
- Captures are copied with `safe_strndup`; callers own returned strings.

Filesystem relevance:
- Shared parsing utility used by version parsing and other libguestfs code that interprets storage/device strings.
