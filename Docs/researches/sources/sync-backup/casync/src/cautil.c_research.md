# sources/sync-backup/casync/src/cautil.c

## Purpose

`cautil.c` provides small casync-specific utility functions for classifying locators, normalizing file URLs, checking locator suffixes, filtering xattr names, selecting the compressed chunk suffix, and replacing the last path component of path/SSH/URL locators. These utilities are used by higher-level code that accepts path-like, SSH-like, or URL-like user inputs.

## Important APIs, Types, and Functions

`ca_is_definitely_path()` is private and treats absolute paths plus `.`, `..`, and `./...` as filesystem paths. `ca_is_url()` recognizes restricted RFC3986-style URLs that contain `://`, a protocol character set, and a non-empty host/path separator, while excluding definite paths. `ca_is_ssh_path()` recognizes `host:path` and `user@host:path` forms while excluding definite paths and empty remote path components. `ca_classify_locator()` returns `CA_LOCATOR_URL`, `CA_LOCATOR_SSH`, `CA_LOCATOR_PATH`, or invalid for empty input.

`ca_strip_file_url()` converts `file:///...` and `file://localhost/...` to local paths and percent-decodes hex escapes defensively; other inputs are duplicated unchanged. `ca_locator_has_suffix()` checks suffixes for URLs before query/parameter delimiters and for paths/SSH locators only against the final path component, requiring the suffix not to be the entire component. `ca_xattr_name_is_valid()` enforces non-empty, contains-dot, no leading/trailing dot, and `<=255` length. `ca_xattr_name_store()` permits only valid `user.` and `trusted.` xattrs for generic storage. `ca_compressed_chunk_suffix()` returns `CASYNC_COMPRESSED_CHUNK_SUFFIX` or `.cacnk` and caches the returned pointer. `ca_locator_patch_last_component()` replaces the basename component for URL, SSH, and path locators while preserving URL scheme/host and SSH prefix.

## Control Flow

Locator classification first rejects empty strings, then checks URL syntax before SSH syntax, defaulting to path. Last-component patching switches on that class: URLs skip protocol/host and query/parameter suffixes before finding the final slash; SSH paths split at `:` and use `dirname_malloc()` if the remote path has slashes; filesystem paths use `dirname_malloc()` when there is a slash or else replace the whole locator.

## State and Persistence Behavior

Most functions are pure string transforms that allocate new strings for callers to free. `ca_compressed_chunk_suffix()` has one static cached pointer and observes the environment only on first call. `ca_strip_file_url()` and `ca_locator_patch_last_component()` allocate results with `strdup`, `new`, or `strjoin`.

## Dependencies and Integration Points

This file depends on `util.h` for helpers such as `startswith`, `endswith`, `isempty`, `unhexchar`, `strjoin`, `strndupa`, `dirname_malloc`, and character sets. `casync.c` uses locator classification to route archive/index/store inputs to local or remote setters. Store and archive code likely use the compressed chunk suffix and xattr filters.

## Risks and Edge Cases

The URL parser is intentionally restrictive and may classify unusual but valid URLs as paths. The SSH parser treats any `host:path` with allowed host characters and non-empty suffix as SSH, so Windows-style drive letters can be ambiguous unless they are definite paths. `ca_strip_file_url()` decodes percent escapes byte-wise without validating UTF-8 and leaves non-localhost file URLs unchanged. The compressed suffix cache means changing the environment after first use has no effect. URL suffix handling ignores text after `?` or `;`, which must match remote URL conventions.

## Test Signals

Tests should cover absolute paths, `.`, `..`, relative names, `./x`, `http://host/path`, URL queries/parameters, `file:///tmp/a%20b`, `file://localhost/tmp`, non-local file URLs, `host:path`, `user@host:path`, empty remote components, Windows-like strings if supported, suffix checks for final components and URLs with query strings, xattr namespace filtering, and last-component patching for each locator class.
