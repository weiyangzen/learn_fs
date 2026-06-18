# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/idmap.c

Implements user/group name-to-id and id-to-name maps for CIFS shares.

Key points:
- `Idmap` is a hash table of `Ident` records linked both by id hash and name hash.
- `name2id` and `id2name` perform lookup by name/id.
- `idmap` inserts one mapping into both hash chains.
- `readidmap` reads either Unix-style `/etc/passwd`/`/etc/group` or Plan 9 `/adm/users` style files.
- Unix style extracts name and numeric id from colon-separated records.
- Plan 9 style offsets numeric ids by 9,000,000 and extracts names from `/adm/users` records.
- `unixidmap` tries share-local `etc/passwd` and `etc/group`, then share-local `adm/users`, otherwise installs empty maps.
- `unixname`, `unixuid`, and `unixgid` expose lookup helpers.

Dependencies and interactions:
- `Share` objects hold user and group maps.
- Uses `namehash` from utility code.

Research relevance:
- Provides ownership name/id translation for CIFS Unix extensions or file metadata presentation.
