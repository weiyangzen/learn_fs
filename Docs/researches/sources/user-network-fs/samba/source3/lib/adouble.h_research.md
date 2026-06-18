# sources/user-network-fs/samba/source3/lib/adouble.h

Purpose: declares the AppleDouble public contract used by vfs_fruit and related Samba VFS code.

Important APIs/types/functions: defines `adouble_type_t`, AppleDouble magic/version/entry identifiers, Netatalk xattr names, fixed entry lengths, sharemode lock offsets, date conversion macros, conversion flags, opaque `struct adouble`, `struct adouble_buf`, and APIs for reading/writing entries, dates, conversion/unconversion, sidecar naming/opening, AFP info packing/unpacking, and raw buffer parsing.

Control flow: callers choose `ADOUBLE_META` for Netatalk metadata xattrs or `ADOUBLE_RSRC` for resource sidecar files, then use `ad_get()/ad_fget()`, mutate entry pointers/lengths or date fields, and persist with `ad_fset()`. Higher-level conversion flows call `ad_convert()` or `ad_unconvert()` with CATIA mappings and flags.

State and persistence: the header exposes persistent wire/layout constants rather than storage itself. Date macros translate between AppleDouble network-order time and Unix time using `AD_DATE_DELTA`.

Dependencies/integration: includes `MacExtensions.h`, relies on Samba `DATA_BLOB`, `TALLOC_CTX`, `vfs_handle_struct`, `files_struct`, and `smb_filename` declarations from surrounding includes.

Risks/test signals: constants are ABI/file-format sensitive; changing lengths, IDs, lock offsets, or xattr names breaks stored metadata and locking semantics. Test callers should verify compile-time consumers see consistent entry IDs, date conversions, `HAVE_ATTROPEN` xattr naming, and sidecar name behavior for root and nested paths.
