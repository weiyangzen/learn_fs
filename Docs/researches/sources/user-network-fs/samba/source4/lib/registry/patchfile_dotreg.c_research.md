# sources/user-network-fs/samba/source4/lib/registry/patchfile_dotreg.c

`patchfile_dotreg.c` saves and loads Windows `REGEDIT4` `.REG`-style registry diffs. Save-side callbacks write key headers, delete-key headers, value assignments, and delete-value lines. `reg_val_dotreg_string()` converts registry data to strings: UTF-16 strings become Unix strings, DWORDs become eight-digit hex, binary data becomes comma-separated bytes, and other types use `hex(type):...`. `reg_dotreg_diff_load()` parses line-oriented `.REG` input and invokes registry diff callbacks.

Parser control flow skips the first header line, tracks the current key, supports key deletion with `[-key]`, value deletion with `=-`, line continuation with trailing backslash and two-space continuation, and uses `reg_string_to_val()` for data conversion.

Persistence occurs through callbacks, usually `reg_diff_apply()`. Risks include documented lack of newer UCS-2 `.REG` support, fragile quoting and default-value handling, clearing `curkey` on blank/comment lines, mode `0755` for created patch files, limited escaping on save, and non-transactional application. Tests should include REG_SZ, DWORD, binary, default `@`, multiline hex, delete value/key, comments, CRLF input, and malformed lines.
