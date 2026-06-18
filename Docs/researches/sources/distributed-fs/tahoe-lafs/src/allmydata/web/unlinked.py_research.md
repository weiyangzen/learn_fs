# sources/distributed-fs/tahoe-lafs/src/allmydata/web/unlinked.py

## Purpose
Implements `/uri` operations that create Tahoe objects without linking them into an existing directory. It supports PUT/POST uploads of immutable CHK and mutable SDMF/MDMF files, mutable directories, directories with initial children, immutable directories, upload-result pages, and optional redirects.

## Important APIs, Types, And Functions
Creation helpers are `PUTUnlinkedCHK`, `PUTUnlinkedSSK`, `PUTUnlinkedCreateDirectory`, `POSTUnlinkedCHK`, `POSTUnlinkedSSK`, `POSTUnlinkedCreateDirectory`, `POSTUnlinkedCreateDirectoryWithChildren`, and `POSTUnlinkedCreateImmutableDirectory`. `UploadResultsPage` and `UploadResultsElement` render multipart CHK upload results and reuse `status.UploadResultsRendererMixin` for share/timing details.

## Control Flow
`root.URIHandler` dispatches PUT/POST `/uri` requests here after parsing `format`/`mutable`. PUT reads from `req.content`; POST reads multipart `req.fields["file"].file` for uploads or request body JSON for directory children. CHK uploads call `client.upload(FileHandle(...))`; mutable uploads call `client.create_mutable_file(MutableFileHandle(...))`; directory creation calls `client.create_dirnode` or `client.create_immutable_dirnode`. `when_done` on CHK multipart upload can redirect to a URL after substituting `%(uri)s`; `redirect_to_result=true` on directory creation sends a 303 to `uri/<newcap>`.

## State And Persistence
The module does not keep local state. Persistent effects are new Tahoe objects on the grid: immutable files, mutable files, mutable directories, and immutable directories. Optional `private-key` arguments are parsed via `get_keypair` for deterministic mutable object keypairs. Upload result resources hold an in-memory upload result object only long enough to render the response.

## Dependencies And Integration Points
It depends on Twisted HTTP/templates/resources, Tahoe `FileHandle` and `MutableFileHandle`, common helpers for format parsing, children JSON conversion, redirects, keypair parsing, and status upload-result rendering. It is reached exclusively through `root.URIHandler` for top-level `/uri` creation operations.

## Risks And Test Signals
Risks include multipart field assumptions (`file` must exist), content-type heuristics for distinguishing `t=mkdir` from `t=mkdir-with-children`, URL quoting and open redirect behavior through `when_done`, bytes/str substitution for `%(uri)s`, rejecting `format=CHK` for directories, and inconsistent use of `unique_keypair` between PUT/POST mutable file creation. Tests should cover all `/uri` PUT/POST creation variants, `format` and `mutable` combinations, bad children JSON/body rejection, redirect behavior, upload-result rendering, private-key handling, and resulting capability usability.
