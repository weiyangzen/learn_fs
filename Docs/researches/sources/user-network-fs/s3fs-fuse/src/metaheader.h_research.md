# sources/user-network-fs/s3fs-fuse/src/metaheader.h

## Purpose
Declares the case-insensitive HTTP/object metadata header map and the conversion utilities that turn object metadata into s3fs filesystem attributes and object-type decisions.

## Important APIs, Types, And Functions
`headers_t` is `std::map<std::string, std::string, case_insensitive_compare_func>`, matching HTTP header case-insensitivity. The API exposes time extraction (`get_mtime`, `get_ctime`, `get_atime`), size/mode/owner/group parsing, object format probes (`is_reg_fmt`, `is_symlink_fmt`, `is_dir_fmt`), `derive_object_type()`, block count calculation, IAM and Last-Modified timestamp parsing, `is_need_check_obj_detail()`, `merge_headers()`, and `convert_header_to_stat()`.

## Control Flow
The header is pure declarations and default arguments. Defaults are significant: time getters overcheck by falling back to Last-Modified, `get_mode()` does not check directory markers unless requested, `derive_object_type()` defaults to `UNKNOWN`, and `convert_header_to_stat()` does not force directory mode unless told.

## State And Persistence Behavior
No state is owned by the header. All persistence semantics are caller-driven through HTTP headers and resulting stat/cache metadata. `headers_t` ordering is stable by case-insensitive key comparison, which affects deterministic iteration in callers such as header merging.

## Dependencies And Integration Points
The header depends on `types.h` for `case_insensitive_compare_func` and `objtype_t`, plus standard `map`, `string`, and `sys/stat.h`. It is a central metadata API for the FUSE layer, cache layer, curl response handling, and thread request code.

## Risks
Default arguments can hide important behavior: callers may unknowingly accept Last-Modified fallback as real atime/ctime/mtime, or may fail to enable directory checks when inferring modes. Because `headers_t` is case-insensitive, inserting differently cased duplicate keys overwrites by comparator equivalence, which is desirable for HTTP but should be understood in merge tests.

## Test Signals
Compile and unit tests should verify `headers_t` case-insensitive lookup and overwrite behavior, default argument behavior, and conversion API results for S3, GCS, and s3sync metadata conventions. Integration tests should confirm FUSE `getattr`, `readdir`, rename, symlink, and directory placeholder flows use the expected defaults.
