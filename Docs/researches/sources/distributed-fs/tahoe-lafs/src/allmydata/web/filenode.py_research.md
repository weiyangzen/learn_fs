# sources/distributed-fs/tahoe-lafs/src/allmydata/web/filenode.py

## Purpose
Implements WebAPI resources for file nodes and placeholder leaf nodes. It handles file downloads, metadata/capability views, immutable replacement, mutable overwrite/update, form uploads, child-cap replacement, checks/repairs, deletion from a parent directory, byte-range GET/HEAD responses, and JSON metadata generation.

## Important APIs, Types, And Functions
`ReplaceMeMixin` contains shared replacement helpers: `replace_me_with_a_child`, `replace_me_with_a_childcap`, and `replace_me_with_a_formpost`. `PlaceHolderNodeHandler` handles writes to a not-yet-existing child. `FileNodeHandler` handles existing files with `getChild`, `render_GET`, `render_HEAD`, `render_PUT`, `render_POST`, `render_DELETE`, `replace_my_contents`, `update_my_contents`, and form overwrite helpers. `FileDownloader` parses Range headers and streams file bytes. `_file_json_metadata`, `_file_uri`, `_file_read_only_uri`, and `FileNodeDownloadHandler` support alternate routes and `/file/<cap>/...` downloads.

## Control Flow
Directory traversal returns a placeholder when a leaf does not exist but a PUT/upload can create it. Replacement chooses immutable CHK upload through `FileHandle` and `parentnode.add_file` or mutable SDMF/MDMF creation through `MutableFileHandle` and `client.create_mutable_file`, optionally using `get_keypair`. Existing file `GET` without `t` obtains the best readable version and returns a `FileDownloader`; `GET t=json` may refresh mutable servermap before reading edge metadata; `t=info`, `uri`, and `readonly-uri` return specialized resources or text. PUT to mutable files overwrites or updates at a nonnegative offset, while PUT to immutable files replaces the parent link. POST supports check and multipart upload. Download rendering sets content type, content disposition, range headers, content length, and delegates streaming to `filenode.read`.

## State And Persistence
Handlers retain client, node, parentnode, and name. Persistent effects are all delegated to Tahoe nodes and parent directories: uploads create immutable files, mutable files are created or overwritten, mutable versions can be updated at an offset, child links can be set or deleted, and check/repair can add leases. Download state is request-local; `FileDownloader` holds the readable filenode/version and filename. ETags are emitted for immutable fixed outputs based on storage index and output type.

## Dependencies And Integration Points
The module depends on Twisted HTTP/static resources, Tahoe upload and mutable publish handles, mutable read mode, blacklist/prohibited-node wrappers, monitor checks, check result renderers, `MoreInfo`, and shared argument/error helpers. It is used by `directory.make_handler_for`, `/file` via `root.FileHandler`, and directory upload delegation. Its metadata shape feeds WebAPI clients expecting `filenode` JSON tuples with caps, verify caps, mutability, format, size, and edge metadata.

## Risks And Test Signals
Risk areas include Range parsing edge cases, single-range-only behavior, lack of Content-Range support for PUT, offset parsing raising raw `ValueError`, readonly mutable replacement rejection, bytes/str handling for filenames and content-disposition, and weak error signaling after streaming has already started. `replace` is parsed as `only-files` in PUT but as boolean for some POST paths. Test signals include WebAPI upload/download tests in `src/allmydata/test/web/test_web.py`, range GET/HEAD coverage, mutable overwrite/update tests, JSON metadata tests, prohibited-node behavior, ETag behavior for immutable files, and check/repair rendering through `test_checker.py`.
