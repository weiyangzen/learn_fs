# sources/user-network-fs/samba/source4/torture/raw/chkpath.c

Purpose: This file tests SMB1 `CHKPATH` behavior and compares it with pathinfo, findfirst, and open behavior for path normalization, invalid names, dot segments, bad characters, and DOS/NT status compatibility.

Important APIs, types, and functions: `single_search()` runs a one-result `RAW_SEARCH_TRANS2`. `test_path_ex()` issues `smb_raw_chkpath()` and `RAW_FILEINFO_NAME_INFO` pathinfo, compares expected statuses, and optionally checks normalized returned names. `test_chkpath()` covers many concrete path cases. `test_chkpath_names()` iterates ASCII bytes 0x01 through 0x7f in filenames. `torture_raw_chkpath()` sets up the test tree.

Control flow: The suite creates `\\rawchkpath`, nested `nt\\V S\\VB98`, and a file named `vb6.exe`. It checks existing and missing paths, hidden directory lookup, redundant slashes, parent references, invalid dot-only paths, attempts to traverse through files, wildcard components, root paths, and open/findfirst status parity for selected ambiguous paths. The name loop classifies control characters and reserved characters as invalid while allowing ordinary printable bytes.

State and persistence behavior: It creates and deletes only the `\\rawchkpath` tree and temporary files. No persistent state is intended after `smbcli_deltree()`.

Dependencies and integration points: The test depends on raw SMB `CHKPATH`, pathinfo, search, NT create, `torture_set_file_attribute()`, locale `isprint()`, and torture settings such as `samba4-ntvfs` for known name normalization differences.

Risks: Expected statuses allow both NT and DOS mapped variants, but filesystem and server path parser differences can still cause failures. Slash handling is conditional because Samba FS treats `/` like `\\` outside `samba4-ntvfs`.

Test signals: Passing tests show that path validation, canonical name reporting, reserved-character rejection, dot/parent handling, wildcard rejection, and error-code mapping match Samba's expected SMB1 behavior.
