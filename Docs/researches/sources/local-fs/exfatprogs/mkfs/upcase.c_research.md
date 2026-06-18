# File Research: sources/local-fs/exfatprogs/mkfs/upcase.c

`upcase.c` writes the exFAT upcase table during filesystem creation.

`exfat_create_upcase_table()` writes `ui->upcase.table` of length `ui->upcase.len` to `finfo.target.byte.ofs + finfo.ut_byte_off`. When write verification is enabled, it rereads and compares the upcase table.

After writing the table bytes, it zero-fills the gap from the end of the table to the root directory offset:
- `zero_ofs = target + upcase offset + upcase length`
- `zero_len = root offset - upcase offset - upcase length`

It also verifies that zero-fill region when requested. On verification failure, it prints a specific upcase table mismatch error and returns the underlying error code.

The function asserts that the root directory offset is at or after the upcase-table offset, depends on the global `finfo` layout from `mkfs.c`, and uses libexfat full-write, zero-write, and verification helpers.
