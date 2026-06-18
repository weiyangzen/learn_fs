# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_from_text_nfs4.c

NFSv4 ACL text-entry parser used by `acl_from_text()`. It parses tags such as `owner@`, `group@`, `everyone@`, `user`, and `group`, optional qualifiers, access masks, optional flags, entry types (`allow`, `deny`, `audit`, `alarm`), and optional appended numeric ids for unresolved names.

The parser creates an entry first, fills it through public ACL setters, and deletes the entry on malformed or truncated input. Name resolution uses `_acl_name_to_id()`, and unresolved user/group names require an appended id field.
