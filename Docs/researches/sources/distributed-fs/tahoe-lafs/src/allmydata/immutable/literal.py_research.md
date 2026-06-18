# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/literal.py

## Purpose

This module implements in-memory immutable file nodes backed by literal file capabilities. Literal files are small files whose bytes are embedded directly in the URI, so they do not have storage indexes, shares, verify caps, or repair work. The node exposes the same high-level immutable file interface as CHK-backed immutable files so directory and web/download code can treat literal nodes uniformly.

## Important APIs, Types, and Functions

- `_ImmutableFileNodeBase` provides common immutable node identity and capability behavior: no write URI, read-only URI equals `get_uri`, immutable/read-only flags, immutable-directory eligibility, no-op `raise_error`, and URI-based equality/hash.
- `LiteralFileNode` implements `IImmutableFileNode` and `ICheckable`.
- `LiteralFileNode.__init__(filecap)` requires a `LiteralFileURI`.
- `get_size`, `get_current_size`, `get_cap`, `get_readcap`, `get_verify_cap`, `get_repair_cap`, `get_uri`, and `get_storage_index` expose literal metadata. Verify/repair caps and storage index are always `None`.
- `check` and `check_and_repair` immediately succeed with `None`.
- `read(consumer, offset=0, size=None)` slices embedded bytes and streams them into a Twisted consumer through `basic.FileSender`.
- `get_best_readable_version`, `download_best_version`, `download_to_data`, and `get_size_of_best_version` provide the readable-file compatibility surface.

## Control Flow

Construction wraps a `LiteralFileURI`. Reads are purely local: the requested byte range is sliced from `self.u.data`, wrapped in `BytesIO`, and passed to `FileSender.beginFileTransfer`. The returned deferred maps back to the consumer object. Download-to-data bypasses streaming and immediately returns the embedded bytes. Check and repair paths avoid network or storage checks and return already-fired deferreds.

## State and Persistence Behavior

The only state is `self.u`, the literal URI object containing the bytes. There is no local or remote persistence beyond the URI string itself. Equality and hashing derive from the URI object, so two literal nodes with the same embedded cap compare equal.

## Dependencies and Integration Points

The module depends on Twisted `Deferred`s and `FileSender`, the `IImmutableFileNode`/`ICheckable` interfaces, and `allmydata.uri.LiteralFileURI`. `nodemaker.py` constructs `LiteralFileNode` for literal caps. `upload.LiteralUploader` creates literal caps for data at or below `Uploader.URI_LIT_SIZE_THRESHOLD` and returns upload results with no sharemap/servermap. Directory, filenode, web, and system tests use this node wherever immutable file nodes are expected.

## Risks and Edge Cases

- `check` and `check_and_repair` return `None`, not a rich check result; callers must tolerate literal nodes as trivially local.
- `get_storage_index`, verify cap, and repair cap are `None`; code that assumes all immutable nodes are CHK-backed will break.
- `read` slices the embedded data before handing it to `FileSender`. This is fine for literal caps because they are intentionally tiny, but the implementation would not be appropriate for large embedded payloads.
- `raise_error` is a no-op, matching the absence of deferred latent errors; callers should not expect it to validate cap contents.

## Test Signals

`src/allmydata/test/test_immutable.py` contains `LiteralFileNodeTests` for URI-based equality. `test_filenode.py`, `test_dirnode.py`, and `test_system.py` also instantiate literal nodes in broader filesystem flows. Upload behavior that chooses literal caps is covered through `upload.LiteralUploader` and small-file upload paths in `test_upload.py`.
