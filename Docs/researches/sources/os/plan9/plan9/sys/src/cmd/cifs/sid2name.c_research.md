# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/sid2name.c

Maps Windows SIDs to shorter owner/group names for Plan 9 `Dir` fields. Contains well-known local user/group, domain user/group, and alias RID mappings.

`upd_names` opens a file with `READ_CONTROL`, queries owner/group SIDs via `TNTquerysecurity`, maps them through `sid2name`, and updates `Dir.uid`/`Dir.gid`; failures fall back to `"unknown"`.
