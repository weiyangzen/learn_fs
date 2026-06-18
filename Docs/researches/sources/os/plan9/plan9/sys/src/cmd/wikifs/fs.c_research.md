# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/fs.c

This file implements the `wikifs` 9P server. It exposes wiki pages, versions, generated HTML/text views, history, diffs, edit forms, error pages, and page creation.

Filesystem model:
- Root contains:
  - `new`: write-only-ish page creation endpoint.
  - `map`: title-to-number lookup endpoint.
  - One directory per page, walkable by numeric id or title.
- Page directory contains files:
  - `index.html`, `index.txt`, `current`, `history.html`, `history.txt`, `diff.html`, `edit.html`, `werror.html`, `werror.txt`, `.httplogin`.
  - History subdirectories named by timestamp expose old `index.html`, `index.txt`, and `current`.

Qid encoding:
- Qid path packs 8-bit type, 16-bit page number, 16-bit page version/index, and 8-bit file index.
- Types: `Droot`, `D1st`, `D2nd`, `Fnew`, `Fmap`, `F1st`, `F2nd`.

Walk/materialization:
- `fswalk1` resolves root entries, page dirs, history dirs, and generated files.
- On walking generated files, it eagerly renders into `Aux.s` using `tohtml`, `totext`, or raw document formatting.
- History/diff files force loading full history via `gethistory`.

Open/read/stat:
- `fsopen` enforces read-only access except `new` and `map`, snapshots current map for root reads, loads history for page dir opens, and initializes `new` write buffer.
- `fsread` generates directory listings or reads materialized strings.
- `fsstat` synthesizes metadata from qid and cached string length.

Write behavior:
- Writing to `map` maps a title/name to page number and stores it in `Aux.n`.
- Writing to `new` appends content until a zero-length write commits.
- Commit format expects title line, optional metadata lines (`A`, `D`, `C`), blank separator, and wiki body.
- It parses body with `Brdpage`, allocates/reuses page number, formats document text, and calls `writepage`.
- Max new page buffer is `Maxfile`.

Per-fid state:
- `Aux` stores requester name, current `Whist`, selected version index, materialized string, map snapshot, and target page number.
- `fsclone` refcounts `String`, `Whist`, `Map`, and user name across cloned fids.
- `fsdestroyfid` releases all referenced state.

Server startup:
- Options include `-D`, listen addresses, mountpoint/service, permission override, and no-mount mode.
- Validates wiki directory, initializes map, registers listeners, posts mount with create support, and optionally chmods `/srv/<service>`.

Notable behavior:
- Generated content is produced at walk time, so repeated reads use the fid's snapshot.
- Write conflicts are detected in `writepage`, and conflicting writes are appended to history but not installed as current.
