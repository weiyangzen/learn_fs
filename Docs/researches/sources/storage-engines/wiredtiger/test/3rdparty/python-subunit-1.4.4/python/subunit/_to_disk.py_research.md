# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/_to_disk.py

## Purpose

`_to_disk.py` exports a subunit v2 stream into a directory tree: one directory per test id, one `test.json` metadata file, and one file for each attachment/detail.

## Important APIs, Types, and Functions

`_allocate_path(root, sub)` normalizes a requested path under a root, prevents parent-directory escape by rewriting separators, and appends numeric suffixes for collisions. `_open_path(root, subpath)` creates parent directories and opens a binary file. `_json_time()` stringifies optional timestamps. `DiskExporter.export(test_dict)` writes metadata and detail files. `to_disk(argv=None, stdin=None, stdout=None)` is the CLI entry point.

## Control Flow

`to_disk` parses `--directory` and an optional input filename. It creates a `DiskExporter`, wraps `export` with `testtools.StreamToDict`, then calls `run_tests_from_stream` with `protocol_version=2`. `StreamToDict` accumulates per-test status data and calls `export` when complete. `DiskExporter.export` allocates a root for the test id, writes sorted metadata to `test.json`, then iterates each detail content's bytes to sibling files under that root.

## State and Persistence Behavior

This module is persistence-oriented. It creates directories and binary files under the configured export directory. Collision handling creates suffixes such as `foo-1`. Escape prevention compares `realpath` values and rewrites unsafe subpaths, reducing traversal risk from malicious test ids or attachment names.

## Dependencies and Integration Points

It depends on `testtools.StreamToDict`, `subunit.filters.run_tests_from_stream`, JSON, and the filesystem. The thin CLI wrapper is `filter_scripts/subunit2disk.py`.

## Risks and Test Signals

Path safety is the main risk. The prefix check uses `candidate.startswith(realroot)`, which can be vulnerable to sibling-prefix confusion if not followed by a path separator, although unsafe paths are later rooted through recursive rewriting only when the prefix check fails. Large attachments are streamed chunk by chunk but still materialized by `StreamToDict` semantics before export. `test_filter_to_disk.py` smoke-tests JSON metadata and attachment content for a successful tagged test.
