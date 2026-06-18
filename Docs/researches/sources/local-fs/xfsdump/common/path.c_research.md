# File Research: sources/local-fs/xfsdump/common/path.c

## Role

This file implements pathname helper functions for relative-to-absolute conversion, normalization, prefix tests, and path difference extraction.

## Public Functions

`path_beginswith()` checks whether `path` begins with `base`.

`path_diff()` returns a newly allocated suffix of an absolute path relative to an absolute base, or null if the path does not begin with the base or has no suffix.

`path_reltoabs()` converts a local relative path into `basedir/path`, normalizes local paths, and preserves remote-style paths containing `:`.

`path_normalize()` canonicalizes absolute paths by removing empty components and `.`, and resolving `..` unless it would escape above root.

## Internal Model

The implementation tokenizes a path with `pem_t`, stores accepted path elements in a fixed-size `pa_t` array, peels entries for `..`, then generates a normalized absolute pathname.

## Limits And Assumptions

- `path_normalize()` asserts paths are absolute.
- The element array has a fixed maximum of 1024 components.
- Returned strings are heap allocated.
- Remote paths are detected only by the presence of `:`.
