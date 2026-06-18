# sources/storage-engines/foundationdb/bindings/python/tests/directory_extension.py

Purpose: This module adapts the language-agnostic binding tester stack machine to Python directory-layer and subspace operations.

Important APIs and types: `DirectoryExtension` maintains `dir_list`, active `dir_index`, and `error_index`. `process_instruction` handles `DIRECTORY_CREATE_SUBSPACE`, `DIRECTORY_CREATE_LAYER`, create/open/move/remove/list/exists operations, pack/unpack/range/contains, logging, subspace opening, and prefix stripping.

Control flow: Instructions pop tuple-encoded paths and parameters from the tester stack, invoke the selected directory or subspace object, append new directory handles when operations create or open one, and push results back as raw values or tuple-packed data. Exceptions push `DIRECTORY_ERROR`; operations that would create a directory append `None` so later indexed operations remain deterministic.

State and persistence behavior: The extension stores only in-memory handles, but operations mutate persistent FoundationDB directory metadata through `fdb.directory_impl` calls. Logging operations write directory state into caller-provided subspaces.

Dependencies and integration points: It depends on `fdb`, `fdb.directory_impl`, `fdb.Subspace`, and the `Instruction`/`Stack` protocol in `tester.py`. It mirrors the Ruby directory extension to support cross-binding conformance tests.

Risks: Stack order and path tuple decoding must match the tester spec exactly. Exceptions are intentionally flattened to `DIRECTORY_ERROR`, which is good for conformance but can hide diagnostic detail unless logging flags are enabled.

Test signals: Binding tester directory op streams validate creation, manual-prefix behavior, partitions, moves, removals, list/existence, key packing, range boundaries, containment, logging, and error handling.
