# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_grid.py

## Purpose
This is the main web-API/grid integration suite for Tahoe-LAFS. It exercises file check/repair, deep check, stream manifest, add-lease behavior, error rendering, unknown cap rendering, immutable-directory mutant filtering, blacklist enforcement, and web exception content negotiation against no-network Tahoe grids.

## Important APIs, Types, And Functions
`ErrorBoom` is a resource decorated with `render_exception` that raises `CompletelyUnhandledError` for error-rendering tests. `Grid` mixes `GridTestMixin`, `WebErrorMixin`, `ShouldFailMixin`, `ReallyEqualMixin`, and `AsyncTestCase`. Helper methods `CHECK` and `GET_unicode` issue web requests against grid clients. The tests use `UnknownNode`, `CorruptShareOptions`, `corrupt_share`, `download_to_data`, `split_netstring`, `get_share_file`, `upload.Data`, mutable `publish.MutableData`, URI parsing, blacklist config files, and BeautifulSoup.

## Control Flow
`test_filecheck`, `test_repair_html`, and `test_repair_json` upload healthy, sick, dead, corrupt, literal, and directory objects, then delete or corrupt shares and verify HTML/JSON check and repair responses. `test_unknown` and `test_immutable_unknown` create directories containing future unknown caps, verify listing/info/json behavior, and ensure read-only directory views do not expose write caps. `test_mutant_dirnodes_are_omitted` constructs an immutable directory containing deliberately invalid mutable children, inspects raw netstring data to prove they were stored, then verifies normal listing omits them while preserving valid children.

`test_deep_check` and `test_deep_check_and_repair` build directory trees with immutable, literal, sick, unknown, and unrecoverable children. They assert streaming JSON line order, stats units, recoverability fields, repair fields, and `ERROR:` output for unrecoverable traversal. `test_add_lease` and `test_deep_add_lease` count leases on share files before and after check requests from same or different clients to distinguish lease renewal from new lease addition. `test_exceptions` creates unrecoverable files/directories, bad URIs, missing children, and a failing resource, then checks HTTP status codes, plain-text/HTML body selection, and traceback content. `test_blacklist` edits `access.blacklist`, forces reload behavior, and confirms blacklisted files/directories are denied while parent listings remain usable.

## State And Persistence
The suite creates no-network grids, uploads real shares into temporary server directories, deletes and corrupts share files, counts persisted lease records, and edits the client's `access.blacklist` config file. It mutates in-memory directory nodes, unknown nodes, web roots, blacklist timestamps, and client encoding parameters. Persistence is test-local but uses production share and config file formats.

## Dependencies And Integration Points
The module integrates Tahoe web resources, immutable and mutable upload/publish paths, dirnode serialization, unknown node handling, storage share files, lease records, checker/repairer output, stream-manifest/deep-check APIs, blacklist enforcement, web error handling, content negotiation, and no-network grid helpers. It is a broad end-to-end safety net for user-visible WUI and CLI-facing JSON behavior.

## Risks And Test Signals
Strong signals include health summaries, repair outcomes, JSON field names, unknown-cap privacy, immutable-directory sanitization, stream traversal ordering, stats accounting, unrecoverable error streaming, add-lease semantics, error advice text, status-code mapping, and blacklist inheritance. Risks include brittle HTML/body substring assertions, direct dependence on share file layout and lease internals, long Deferred chains that can obscure failures, and test coverage concentrated on synthetic no-network grids rather than real HTTP deployment.
