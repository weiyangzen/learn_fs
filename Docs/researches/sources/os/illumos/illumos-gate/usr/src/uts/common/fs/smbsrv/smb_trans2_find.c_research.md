# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_find.c

Implements SMB1 `TRANS2_FIND_FIRST2`, `TRANS2_FIND_NEXT2`, and `FIND_CLOSE2` directory enumeration. The file supports legacy and NT-style information levels, resume keys, close-on-EOS flags, backup intent, access-based enumeration interactions through lower layers, and exact wire encoding of returned entries.

`smb_find_args_t` carries fixed response size, info level, max count, flags, EOS state, last-name offset, and last resume key/name across enumeration helpers. `smb_trans2_find_max` limits the number of entries returned per request.

`FindFirst2` validates disk share use, decodes search attributes/count/flags/info level/path, rejects stream names, optionally switches to privileged backup credentials, computes fixed entry size, opens an `smb_odir_t`, encodes entries, handles no-match as `NT_STATUS_NO_SUCH_FILE`, optionally closes the search, and returns SID/count/EOS/EA error/last-name offset.

`FindNext2` decodes the existing search ID, count, info level, resume key, flags, and resume filename. It looks up the open directory through the tree with same-user enforcement, chooses continue-from-last or resume-by-name behavior, encodes more entries, optionally closes, and returns count/EOS/EA error/last-name offset. Comments document partial resume-by-name support: the server remembers the last returned name/key pair because arbitrary name resume is not generally possible without sorted directory storage.

`smb_trans2_find_entries` reads `smb_fileinfo_t` entries from the odir, encodes until count or output space is exhausted, patches the final `NextEntryOffset` to zero for modern levels, saves the last returned filename/cookie for future resume, probes one extra entry to detect EOS, and rewinds when an entry was read but not returned. `SMB_INFO_QUERY_EAS_FROM_LIST` currently returns an empty list because EAs are unsupported.

`smb_trans2_find_mbc_encode` handles all supported information levels, including legacy standard/EA-size, directory/full/id/both/name variants, and Mac HFS info sizing. It computes ASCII/Unicode name lengths, null terminators, 4-byte padding for modern levels, optional resume keys, 32-bit truncation for old size fields, short-name encoding, node IDs, timestamps, DOS attributes, and last-name offsets.

`FIND_CLOSE2` decodes the search ID, looks it up on the current tree, closes/releases the odir, and returns an empty SMB result.
