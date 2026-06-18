# sources/user-network-fs/libfuse/lib/modules/iconv.c

Purpose: `modules/iconv.c` implements a high-level libfuse stackable module that converts file paths and directory entry names between a user-facing charset and the underlying filesystem charset.

Important APIs, types, and functions: `struct iconv` stores the next filesystem, a mutex, configured charset strings, and two `iconv_t` converters (`tofs` and `fromfs`). `struct iconv_dh` wraps `readdir` filler state. `iconv_convpath` performs locked conversion with dynamic buffer growth. The module wraps nearly every high-level filesystem operation (`getattr`, `access`, `readlink`, directory ops, create/remove/rename/link, chmod/chown/truncate/utimens, open/read/write/statfs, xattr, locks, bmap, lseek, statx). `iconv_init`, `iconv_destroy`, `iconv_help`, `iconv_opt_proc`, and `iconv_new` handle lifecycle and options. `FUSE_REGISTER_MODULE(iconv, iconv_new)` registers the module.

Control flow: For path-based operations, the wrapper converts incoming paths from presentation encoding to filesystem encoding, calls the corresponding `fuse_fs_*` operation on `ic->next`, then frees converted paths. `readlink` and `readdir` convert returned link targets or names back from filesystem encoding before returning to the caller. Module creation parses `from_code` and `to_code`, defaults from UTF-8 to current locale codeset, opens both iconv directions, validates that exactly one lower filesystem is supplied, and creates a `fuse_fs` wrapper.

State and persistence behavior: Converter descriptors and charset strings live for module lifetime and are freed in destroy. A mutex serializes access because `iconv_t` conversion state is mutable. No filesystem data is stored.

Dependencies and integration points: It depends on high-level libfuse stacking APIs, libc/iconv, locale/nl_langinfo, pthread mutexes, and optional `statx`. It is included by Meson only when `HAVE_ICONV` is true and can link either libc iconv or separate libiconv.

Risks: Charset conversion errors return `-EILSEQ`, and path expansion heuristics initially allocate 4x input size but must grow correctly for larger expansions. Locking around shared `iconv_t` is necessary; missing reset on error would poison subsequent conversions, so the error path resets the descriptor. The source currently contains an extra closing brace after `iconv_unlink`, which is a compile-breaking risk if present in the active tree. The error messages in `iconv_open` failure paths appear to swap `from`/`to` in text, which can confuse diagnostics.

Test signals: Tests should mount with different `from_code`/`to_code`, exercise names requiring expansion, invalid byte sequences, readlink/readdir reverse conversion, concurrent path operations, null paths, option help/default locale behavior, and build coverage with and without `HAVE_STATX`.
