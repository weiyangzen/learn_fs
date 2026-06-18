# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/sid2name.c

Adds minimal Windows SID-to-name mapping for Plan 9 directory uid/gid display. The static `known` table maps common well-known local users/groups, domain users/groups, and aliases to short names.

`sid2name` handles nil/malformed SIDs as `-`, exact SID matches, and prefix-plus-RID matches for domain-relative identities. Unknown SIDs are represented by their final RID component.

`upd_names` opens a file with `READ_CONTROL`, queries owner/group security descriptors via `TNTquerysecurity`, converts SIDs, and replaces the `Dir` uid/gid fields. On open failure it uses `unknown`.

Used from `main.c` directory/stat conversion when the `Billtrog` toggle requests real owner/group lookup.

Limitations: no domain controller lookup or SID name service; the mapping is mostly built-in well-known identifiers plus fallback RID display.
