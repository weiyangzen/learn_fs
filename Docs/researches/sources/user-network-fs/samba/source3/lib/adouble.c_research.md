# sources/user-network-fs/samba/source3/lib/adouble.c

Purpose: implements Samba AppleDouble helpers for Netatalk metadata xattrs, `._` resource sidecar files, AFP info packing, and conversion between macOS AppleDouble blobs and Samba alternate-stream storage.

Important APIs/types/functions: private `struct adouble`, `struct ad_xattr_header`, `struct ad_xattr_entry`, `ad_get_entry()`, `ad_getdate()`, `ad_setdate()`, `ad_init()`, `ad_get()`, `ad_fget()`, `ad_fset()`, `ad_convert()`, `ad_unconvert()`, `adouble_open_from_base_fsp()`, `adouble_path()`, `adouble_name()`, `afpinfo_pack()`, `afpinfo_unpack()`, and `adouble_buf_parse()`.

Control flow: allocation chooses fixed Netatalk metadata size or a 64 KiB resource header buffer, `ad_read()` opens/reads metadata or resource state, `ad_unpack()` validates magic/version/entry count/offsets, and `ad_pack()` writes headers plus optional packed xattr blocks before persistence. Conversion pulls xattrs out of oversized FinderInfo into streams, moves resource data back to the canonical offset, optionally wipes blank resource forks, writes FinderInfo to `AFPINFO_STREAM`, and may delete now-empty sidecar files. Unconversion enumerates streams, collects AFP info/resource/general streams, maps stream names through CATIA mappings, deletes converted streams, and writes a rebuilt AppleDouble sidecar.

State and persistence: stores metadata through `SMB_VFS_FGETXATTR/FSETXATTR` on `AFPINFO_EA_NETATALK` or through `pread/pwrite/ftruncate/unlinkat` on `._` files. `struct adouble` owns temporary xattr entry/data buffers and may own an opened `files_struct`, closed by its talloc destructor.

Dependencies/integration: depends on Samba VFS file APIs, `files_struct`, `smb_filename`, stream helpers, AFP constants from `MacExtensions.h`, CATIA/string replacement, byte-order macros, talloc, and root elevation when deleting corrupt metadata xattrs.

Risks: many paths perform multi-step conversion with side effects before final cleanup, so interruption can leave duplicated streams or partially rewritten sidecars. Resource fork relocation allocates the full fork in memory. Bounds checks are extensive, but `adouble_buf_parse()` validates `entries[id]` for duplicates while storing into `entries[i]`, which can misplace parsed entries. Test signals should include corrupt entry offsets/lengths, duplicate IDs, oversized xattr headers, blank resource fork cleanup, readonly fallback, conversion failure cleanup, stream-name mapping, and round-trip AFP info/resource fork preservation.
