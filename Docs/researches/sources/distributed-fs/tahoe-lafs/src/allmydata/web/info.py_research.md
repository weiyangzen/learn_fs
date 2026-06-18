# sources/distributed-fs/tahoe-lafs/src/allmydata/web/info.py

## Purpose
Renders the `t=info` page for files, directories, and unknown nodes. It exposes node type, storage index, size, write/read/verify capabilities, raw download links, check forms, mutable overwrite forms, and directory deep-operation forms.

## Important APIs, Types, And Functions
`MoreInfo` is a `MultiFormatResource` whose HTML and `t=info` renderers flatten `MoreInfoElement`. `MoreInfoElement` provides renderers for title/header/type/storage index, size, directory caps, file caps, raw links, checkability, check form, mutable overwrite form, directory-only deep-check/deep-size/deep-stats/manifest forms, and helper methods `abbrev`, `get_type`, and `get_root`.

## Control Flow
File and directory handlers return `MoreInfo(self.node)` for `GET t=info`. The element class determines node kind through `IDirectoryNode` and `IFileNode`, then fills sections conditionally. Size is asynchronous via `node.get_current_size()` and treats `UnrecoverableFileError` as unknown size. Forms post back to `/uri/<cap>` or the current directory URL with `t=check`, `t=upload`, `t=start-deep-check`, `t=start-deep-size`, `t=start-deep-stats`, or `t=start-manifest`; operation handles are generated from random bytes encoded with base32.

## State And Persistence
The resource stores only the original node. It does not mutate state itself, but it exposes write caps and generates forms that can trigger repair, lease renewal, overwrite, and long-running directory operations. The generated operation handles are request-local random values; resulting operation state is managed by `operations.py` after form submission.

## Dependencies And Integration Points
This module depends on Twisted templates, Tahoe file/directory interfaces, `MDMF_VERSION`, base32, URL quoting, `UnrecoverableFileError`, and the shared `MultiFormatResource`. It integrates with `filenode.py`, `directory.py`, `root.py` routes under `/uri`, and templates in `info.xhtml`. The raw-link generation uses the `/file/<cap>/@@named=/raw.txt` route to avoid directory-context capability exposure.

## Risks And Test Signals
The page intentionally displays capabilities, so access control relies on the surrounding WebAPI threat model. Several renderers reach into `node._node` for directory-backed file caps, making wrapper internals part of this presentation path. Bytes returned from `base32.b2a`/cap methods must flatten correctly in Twisted templates. Tests should cover `t=info` for immutable, mutable, MDMF/SDMF, readonly, LIT, directory, and unknown nodes; size failure handling; form target construction; and integration with deep-operation WebAPI tests.
