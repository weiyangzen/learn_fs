# sources/object-store/rustfs/crates/utils/src/path.rs

## Purpose
Implements object-path and filesystem-path helpers, including MinIO-style directory object encoding, slash normalization, path cleaning, bucket/object splitting, and ETag trimming.

## Important APIs, Types, And Functions
Constants define `GLOBAL_DIR_SUFFIX`, `/`, and `__XLDIR__/`. `is_separator`, `has_suffix`, `has_prefix`, and `strings_has_prefix_fold` handle platform-aware separators/casing. `encode_dir_object`, `is_dir_object`, and `decode_dir_object` translate trailing-slash directory objects to `__XLDIR__`. `retain_slash`, `path_join`, `path_join_buf`, `clean`, `split`, `dir`, `path_to_bucket_object_with_base_path`, `path_to_bucket_object`, `base_dir_from_prefix`, and `trim_etag` provide path manipulation. `LazyBuf` supports allocation-on-change during `clean`.

## Control Flow And State
The module is stateless. `path_join` concatenates components with `/`, detects whether cleaning is needed, and preserves a trailing slash from the final element. `clean` follows Go path-cleaning rules: collapse repeated separators, remove `.`, resolve inner `..`, and keep leading `..` on relative paths. Windows branches treat backslash as a separator and compare prefixes/suffixes case-insensitively.

## Dependencies And Integration Points
Uses `std::path::{Path, PathBuf}` and is exposed under the `path` feature. It is likely consumed by storage layout, bucket/object parsing, and compatibility with MinIO directory-marker semantics.

## Risks And Test Signals
`split` returns `(path, "")` when no separator, which differs from common dirname/basename APIs and is relied on by `dir`. Manual byte-based cleaning assumes separators are ASCII and treats non-ASCII as needing cleaning before copying bytes unchanged. Tests are extensive for Unix-style cleaning, joining, ETag trimming, and Windows-specific separator/unicode cases under Windows cfg.
