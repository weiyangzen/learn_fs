# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/mkhosts.c

Generates legacy host/db/equivalence/text files from ndb entries for a domain.

Key elements:
- Defaults domain to `research.att.com`.
- Parses `/lib/ndb/local` and `/lib/ndb/friends` unless files are provided.
- Collects entries containing `ip` and either matching domain suffix or `ipnet`.
- Stores selected entries in global `X x[4096]`.
- Writes `/lib/ndb/db.<domain>` with DNS-style A/CNAME/MX lines.
- Writes `/lib/ndb/equiv.<domain>` with domain aliases.
- Writes `/lib/ndb/txt.<domain>` with HOST/NET text records.

Notable behavior:
- `printArecord` uses first `dom` as A record and additional `dom`s as CNAMEs.
- `printtxt` uppercases names in place.
- Entries with `flavor=console` are skipped.

Risks and quirks:
- Fixed 4096-entry array has no bounds check.
- Mutates tuple values while uppercasing and trimming `.0` network suffixes.
- Some older host-file generation code is commented out.
