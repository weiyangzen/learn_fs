# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_system.py

## Purpose

This file contains broad Tahoe-LAFS system/integration tests for a multi-node grid. It exercises upload/download, helper-assisted uploads, mutable files, directory nodes, web UI/API routes, command-line operations, checker APIs, connection loss detection, and both Foolscap and HTTP storage-protocol variants.

`SystemTest` inherits from `SystemTestMixin`, `RunBinTahoeMixin`, and Twisted Trial `TestCase`. The same core system tests run with `FORCE_FOOLSCAP_FOR_STORAGE=True`; `HTTPSystemTest` subclasses `SystemTest` with `FORCE_FOOLSCAP_FOR_STORAGE=False`. Likewise `Connections` and `HTTPConnections` cover server connection state under both protocols.

## Important APIs, Types, and Helpers

`RunBinTahoeMixin.run_bintahoe` launches `python -b -m allmydata.scripts.runner` in a subprocess with optional stdin, environment, and Python options via Twisted `getProcessOutputAndValue`. It normalizes signal failures into negative return codes.

`run_cli` wraps `.common_util.run_cli_unicode` with the older inline argument style used by these tests. `do_http` wraps `.common_web.do_http` and decodes response bytes as UTF-8 text.

`CountingDataUploadable` subclasses `upload.Data` to count requested bytes and fire `interrupt_after_d` after a threshold. The resumable-helper test uses it to bounce a helper connection mid-upload.

`_find_all_shares` walks client storage directories and returns `(client_num, storage_index, filename, shnum)` tuples for share files. `_corrupt_mutable_share` reads a `MutableShareFile`, unpacks it with `mutable.layout.unpack_share`, mutates selected fields, repacks, and writes it back. `flip_bit` and `mangle_uri` create corrupted keys/caps for negative download tests.

The HTTP helpers `PUT`, `GET`, `POST`, and `POST2` target `self.webish_url` or `self.helper_webish_url` and construct request bodies, including multipart form data.

`shouldFail` and `shouldFail2` centralize Deferred failure assertions for expected exception types and optional message substrings.

## Control Flow

`_test_upload_and_download` sets up a grid, forces `happy=5`, uploads 4000 bytes with either random-key or convergent encryption, uploads again, downloads through different clients, exercises partial reads, verifies corrupted-key and nonexistent-URI failures, then adds an extra node that uploads through a helper. It covers helper duplicate-upload avoidance for convergent encryption and helper upload interruption/resumption by bouncing client 0 after partial ciphertext fetch. It finally checks helper cleanup and storage stats counters.

`_test_mutable` runs for both SDMF and MDMF. It creates a mutable file, uses `tahoe debug dump-share --offsets` to inspect a share, downloads through cached and newly-created nodes, overwrites contents from different clients, performs an offset update through the async mutable-version API, corrupts SDMF shares in multiple fields while leaving enough shares intact, verifies retrieval, creates empty mutable files, and builds a recursive directory node manifest.

`test_filesystem` builds a small directory tree, bounces a client, verifies access through iterative and path APIs, creates a private directory with read-write and read-only links to another subdirectory, tests read-only mutation failures, moves children around, computes manifest/deep-stats, then calls `_test_web`, `_test_cli`, and `_test_checker`.

`_test_web` checks welcome pages, connection indicators, directory listing, file GET routes, URI-embedded downloads, bogus URI error status 410, PUT upload and replacement including a multi-segment file, unlinked POST uploads with and without helper, operation status pages, helper status HTML/JSON including old incoming/encoding temp files, non-helper helper-status behavior, and statistics HTML/JSON counters.

`_test_runner` finds a CHK share on disk and exercises debug CLI tools: `dump-share --offsets`, `find-shares`, and `catalog-shares`, checking share metadata, verifier cap output, and expected share counts.

`_test_cli` is an extensive inline CLI flow. It verifies `root_dir.cap` compatibility as the default `tahoe:` alias, alias creation/listing, `ls`, `mkdir`, `put` from files and stdin including SDMF format, `get` to stdout/files, `unlink`, `ls -l`, URI and readonly-URI listing, `mv`, `ln`, `cp` between Tahoe and local disk in both directions, overwrite behavior for immutable and mutable targets, recursive copy disk-to-Tahoe, Tahoe-to-disk, caps-only copy, and Tahoe-to-Tahoe recursive copy.

`test_filesystem_with_cli_in_subprocess` verifies a smaller CLI sequence through the actual runner subprocess, including `create-alias`, `put`, `mv` with bogus HTTP proxy environment variables, and `ls`. `_test_checker` validates check/verify behavior for mutable directory nodes, immutable CHK file nodes, and literal file nodes.

`Connections.test_rref` sets up two nodes, records a connected storage server reference, disowns the server service, closes idle HTTP connections, polls until the broker notices only one connected server, and verifies the disconnected server wrapper retains its storage-server object while `is_connected()` becomes false.

## State and Persistence Behavior

The tests create full node directories under `system/SystemTest/...`, including client configs, storage shares, helper working directories, aliases, private root caps, and local files used for CLI copy tests. They intentionally inspect and mutate on-disk share files to validate debug tools, corruption handling, and cleanup of partial uploads.

Upload state spans immutable ciphertext, helper temp directories (`CHK_encoding`, `CHK_incoming`), uploader/downloader/retrieve/publish/mapupdate histories, and stats providers. The helper-resumption scenario depends on partial upload state being cleaned from storage servers and, for convergent uploads, resumable helper state reducing second-upload work.

Mutable file state includes cached node identity, share maps, mutable version updates, sequence/root/hash/signature fields, readonly/writeable caps, and directory manifests/deep stats. CLI state includes aliases and `private/root_dir.cap`.

Connection state is held in storage brokers and remote server wrappers. The HTTP/Foolscap subclasses ensure storage transport selection changes without changing high-level test expectations.

## Dependencies and Integration Points

The file touches much of Tahoe-LAFS: `allmydata.uri`, immutable upload/download/offloaded helper code, mutable share files/layout/publish data, storage server share decoding, node APIs, directory/file interfaces, monitor/checker APIs, web status routes, CLI runner/debug commands, statistics/history providers, and common test system setup.

External libraries include Twisted Deferreds and process utilities, Foolscap errors and eventual scheduling, BeautifulSoup/html5lib for welcome-page inspection, and Python filesystem/process environment APIs.

`SystemTestMixin` is the major harness dependency, providing node setup, `clients`, `numclients`, helper URLs, `add_extra_node`, `bounce_client`, `poll`, `getdir`, and HTTP connection cleanup.

## Risks and Edge Cases

The tests are intentionally long-running and broad. `SystemTest.timeout` is 300 seconds and `test_filesystem.timeout` is 360 seconds, signaling CI slowness risk. Failures can arise from timing, helper reconnection, process environment, network endpoint cleanup, or platform filesystem differences.

The helper-resumption test mutates `offloaded.CHKCiphertextFetcher.CHUNK_SIZE` globally and notes this can affect later helper usage in the same test. Corruption scenarios depend on share counts and 3-of-10 encoding assumptions. Some assertions inspect exact CLI/debug textual output, making them sensitive to wording changes.

Several flows assume UTF-8 text bodies from web routes even when underlying HTTP helpers return bytes. The subprocess CLI test explicitly suppresses Python warnings and validates proxy environment isolation because HTTP proxy variables once affected CLI behavior.

`Connections.test_rref` relies on aggressive timeouts rather than immediate connection refusal because adopted listening file descriptors remain alive after service disowning. Transport-level behavior changes may affect polling duration.

## Test Signals

Passing this file is a strong end-to-end signal that Tahoe nodes can form a grid, upload/download immutable data, handle mutable SDMF/MDMF operations, maintain directory semantics, expose working web/CLI APIs, tolerate helper interruption, produce correct debug/status output, and detect disconnected storage peers under both Foolscap and HTTP storage protocols.

Targeted Trial selections are useful because the full file is expensive: `SystemTest.test_upload_and_download_random_key`, `SystemTest.test_upload_and_download_convergent`, `SystemTest.test_mutable_sdmf`, `SystemTest.test_mutable_mdmf`, `SystemTest.test_filesystem`, `SystemTest.test_filesystem_with_cli_in_subprocess`, `Connections.test_rref`, and their HTTP subclass variants.
