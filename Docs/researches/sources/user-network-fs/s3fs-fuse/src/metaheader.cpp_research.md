# sources/user-network-fs/s3fs-fuse/src/metaheader.cpp

## Purpose
Converts S3/GCS object headers and s3fs metadata headers into filesystem attributes. It parses times, sizes, modes, UID/GID, object type, Last-Modified/IAM expiry timestamps, incomplete metadata detail hints, header merges, and full `struct stat` population.

## Important APIs, Types, And Functions
Time helpers include private `cvt_string_to_time()` and `get_time()`, plus public `get_mtime()`, `get_ctime()`, and `get_atime()`. Attribute parsers include `get_size()`, `get_mode()`, `get_uid()`, `get_gid()`, and `get_blocks()`. Type helpers include private `convert_meta_to_mode_fmt()`, public `is_reg_fmt()`, `is_symlink_fmt()`, `is_dir_fmt()`, and `derive_object_type()`. Date parsers are `cvtIAMExpireStringToTime()` and `get_lastmodified()`. `is_need_check_obj_detail()` decides if a zero-length object may require directory-detail probing. `merge_headers()` overlays metadata maps. `convert_header_to_stat()` builds a `struct stat` from headers.

## Control Flow
Timestamp lookup prefers explicit s3fs metadata (`x-amz-meta-mtime`, `x-amz-meta-ctime`, `x-amz-meta-atime`), supports GCS reserved mtime, and falls back to `Last-Modified` when `overcheck` is true. Mode parsing prioritizes `x-amz-meta-mode`, then s3sync permissions, then GCS POSIX mode, then defaults to 0750 for slash-terminated paths or 0640 otherwise. If file-type bits are absent, directory inference uses forced-dir flags, directory MIME types, slash-terminated zero-size keys, or regular-file fallback. Object type derivation examines only the file-type bits and special folder suffix/path cases. `convert_header_to_stat()` zeroes the stat, sets `st_nlink`, mode, block size, timestamps, size, UID, and GID.

## State And Persistence Behavior
The file is stateless. It consumes `headers_t` maps and emits values or mutates caller-owned maps/stat structures. Defaults use current process effective UID/GID when headers omit ownership, so stat results can vary by runtime user. `merge_headers()` mutates the base map and returns whether anything was updated.

## Dependencies And Integration Points
Dependencies include `metaheader.h`, `string_util.h` for numeric/time parsing, and `filetimes.h` for stat timestamp writes. `headers_t` is a case-insensitive `std::map` declared in the header. Integration is broad: `s3fs.cpp`, `s3fs_threadreqs.cpp`, and `fdcache_entity.cpp` call `convert_header_to_stat()`, `get_mtime()`, `derive_object_type()`, and `is_need_check_obj_detail()` to turn HTTP response headers into FUSE directory entries, attributes, cache metadata, and object-type decisions.

## Risks
`cvt_string_to_time()` parses fractional seconds as the raw digits after the decimal instead of scaling/truncating to nanoseconds; values like `123.45` become `tv_nsec = 45`, not 450,000,000. `convert_header_to_stat()` computes `st_blocks` for regular files before it assigns `st_size`, so regular-file block counts are based on the zeroed size and likely remain zero. `derive_object_type()` dereferences `strpath.rbegin()` without checking for an empty path when the mode is directory. Parsing helpers generally treat malformed numeric strings as whatever `cvt_strtoofft()` returns, with limited validation. Ownership defaults to effective IDs, which can make metadata-less objects appear owned by the mounting user rather than a stable configured identity.

## Test Signals
Tests should feed representative S3, s3sync, and GCS header maps through each parser. Important cases include explicit metadata times, missing metadata with Last-Modified fallback, fractional mtime values, GCS reserved mode/uid/gid, directory MIME types with optional `;charset`, slash-terminated zero-size keys, symlink/file mode bits, metadata-less objects, and forced directory conversion. Regression tests should assert regular-file `st_blocks` follows `Content-Length` and that empty paths are handled safely.
