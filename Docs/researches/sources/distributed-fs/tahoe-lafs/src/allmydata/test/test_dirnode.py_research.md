# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_dirnode.py

## Purpose
This large module tests Tahoe-LAFS directory nodes across mutable SDMF/MDMF directories, immutable directory representations, child packing/unpacking, metadata/timestamp rules, Unicode normalization, unknown future caps, readonly behavior, deep-check/deep-stats integration, retry behavior after uncoordinated writes, overwrite rules, and deterministic directory capability generation from RSA keypairs.

## Important APIs, types, and functions
- `MemAccum` is an `IConsumer` test sink for reading tiny LIT directory children.
- `Dirnode` is the main grid-backed test case. Helpers `_do_create_test`, `_do_initial_children_test`, `_do_basic_test`, `_test_deepcheck_create`, `_do_readonly_test`, and `_do_create_subdirectory_test` drive most directory-node behavior for SDMF and MDMF variants.
- `Packing` tests `dirnode.pack_children`, `DirectoryNode._pack_contents`, `DirectoryNode._unpack_contents`, and deep-immutable enforcement.
- `FakeMutableFile`, `FakeNodeMaker`, and `FakeClient2` provide lightweight mutable-directory tests without a real grid for future/unknown caps.
- `Dirnode2` tests `UnknownNode`, `strip_prefix_for_ro`, and future cap preservation.
- `DeepStats` tests `dirnode.DeepStats`.
- `UCWEingMutableFileNode`, `UCWEingNodeMaker`, and `Deleter` test delete retry after `UncoordinatedWriteError`.
- `Adder` tests overwrite policy including `dirnode.ONLY_FILES`.
- `DeterministicDirnode` tests RSA-keypair-driven deterministic mutable directory caps.

## Control flow
Grid-backed tests create directories through a client `NodeMaker`, then chain Deferred callbacks that mutate children and verify every intermediate result. `_do_create_test` creates a mutable directory, adds mutable children, creates subdirectories, checks list/path lookup/metadata, tests `set_uri`, `set_node`, `set_children`, `set_nodes`, metadata updates, timestamp preservation on replacement, file upload, movement between directories, and `no-write` readonly attenuation. `_do_initial_children_test` creates directories with LIT, CHK, SSK, MDMF, unknown future caps, and LIT directories, then validates normalized child names and readable content. `test_immutable` builds immutable directories and rejects mutable or non-deep-immutable children. Deep-check helpers build a looped tree and assert object counters for healthy and missing-share cases. Tail tests cover packing round trips, future URI handling, stats histograms, retry after upload conflict, overwrite behavior, and deterministic cap derivation.

## State and persistence behavior
Directory state is persisted in mutable file contents encoded as netstrings of child name, read cap, encrypted write-cap data, and metadata. Tests inspect raw `download_best_version` bytes to ensure trailing spaces are preserved in storage while stripped during node creation/listing, and that names are stored/retrieved as Unicode NFC. Metadata state includes user keys plus Tahoe-managed `linkcrtime` and `linkmotime`; tests ensure callers cannot forge Tahoe timestamp fields, creation time is preserved on overwrite, and modification time increases. Share state is persisted in the no-network grid and can be damaged by deleting shares. Deterministic directory tests persist generated caps derived from RSA keypairs through mutable key derivation.

## Dependencies and integration points
The module integrates with Twisted Deferreds, Zope interfaces, Tahoe URI parsing, dirnode implementation, client/node maker APIs, RSA signing key generation and PEM loading, immutable upload/literal nodes, mutable file nodes and key derivation, mutable storage test utilities, no-network grid infrastructure, unknown-node handling, base32/hash helpers, netstring parsing, and Hypothesis. It is one of the core integration suites connecting directory semantics to mutable files, immutable files, cap handling, web-safe readonly attenuation, and deep traversal.

## Risks
The broadest risks are capability safety and data compatibility. Directory packing must preserve unknown future caps without accidentally granting write authority, enforce deep immutability for immutable directories, and keep bytes/unicode names normalized in a stable way across Unicode database changes. Metadata rules are security-sensitive because `no-write` attenuates mutable caps to readonly and Tahoe-managed timestamps must not be caller-controlled. Retry paths around `UncoordinatedWriteError` protect against misleading `NoSuchChildError`. The deterministic keypair tests mean key derivation or serialization changes can alter externally visible caps.

## Test signals
Signals include SDMF/MDMF cap prefixes and backing versions, empty and populated listing behavior, path lookups and missing-child errors, manifest/verifycap/storage-index sets, deep-stats counters and histograms, metadata/timestamp invariants, overwrite rejection and movement semantics, readonly node mutation failures, immutable directory LIT/CHK cap forms, future/unknown cap acceptance and rejection cases, pack/unpack byte-compatible known tree behavior, Hypothesis Unicode round trips, deep-check/deep-repair counters including loops and cache-miss ceiling, delete retry success after forced `UncoordinatedWriteError`, overwrite policy for files versus directories, and deterministic cap equality for known RSA keys.
