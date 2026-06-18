<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/raweas.c -->
# sources/user-network-fs/samba/source4/libcli/raw/raweas.c

Purpose: `raweas.c` serializes and parses SMB extended attribute lists and EA name lists. It supports both classic trans2 EA list format and chained full-EA formats used by NT transact/SMB2-style payloads.

Important APIs, types, and functions: Size/encode helpers include `ea_list_size`, `ea_list_size_chained`, `ea_put_list`, `ea_put_list_chained`, and `ea_push_name_list`. Parse helpers include `ea_pull_struct`, `ea_pull_list`, `ea_pull_list_chained`, and `ea_pull_name_list`; `ea_pull_name` and `ea_name_list_size` are local helpers. The file operates on `struct ea_struct`, `struct ea_name`, `struct smb_wire_string`, and `DATA_BLOB`.

Control flow: Writers compute the exact wire size, fill length headers, flags, name lengths, value lengths, null-terminated names, value data, and chained next-entry offsets with alignment padding. Parsers validate minimum blob sizes, declared total sizes, per-entry name/value lengths, chained `next_ofs` monotonicity, and allocation success, then talloc arrays for output EAs/names.

State and persistence behavior: No durable state is kept. Output arrays, names, and value blobs are allocated beneath the caller's memory context. Parsed EA values are allocated with one extra zero byte and then length is decremented so binary data remains length-tracked while also being safely inspectable as a C string in tests/debugging.

Dependencies and integration points: `rawfile.c` uses EA writers for trans2 mkdir, trans2 open, and NTTRANS create. `rawfileinfo.c` and `rawsearch.c` use EA parsers for EA query/search levels. Server-side SMB/SMB2 parsers and NTVFS paths also reuse these helpers, so this file is shared client/server utility code within the raw layer.

Risks: The size functions assume EA names are strict ASCII and use `strlen`, so embedded NULs or non-ASCII naming rules are not represented. Chained parsing must avoid integer wrap; the code checks `ofs + next_ofs` and `ofs + 4`, but edge cases around zero offsets and malformed padding deserve coverage. Writers assume caller-provided buffers are preallocated to the computed size.

Test signals: EA-related qfileinfo/search tests, SMB2 create EA tests, and server trans2 parser tests are relevant. Useful cases include empty lists, zero-length values, maximum 8-bit name lengths, malformed declared total length, chained offset loops/overflows, and EA list requests that ask for selected names only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/raweas.c -->
