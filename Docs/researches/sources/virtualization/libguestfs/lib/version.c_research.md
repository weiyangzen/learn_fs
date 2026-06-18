# File Research: sources/virtualization/libguestfs/lib/version.c

Version parsing and comparison helpers.

Important behavior:
- Stores explicit version values in `struct version`.
- Parses `X.Y` from arbitrary strings with a default regex or caller-provided regex.
- Can also parse a whole integer as `X.0.0` when allowed.
- Successful parses set major/minor/micro; missing regex match leaves the version unchanged and returns 0.
- `guestfs_int_version_ge` and `guestfs_int_version_cmp_ge` implement lexicographic greater-or-equal comparison.
- Integer parsing uses `xstrtol` and rejects trailing characters.

Filesystem relevance:
- Shared feature-gating utility for external tools and backends whose behavior depends on parsed version numbers.
