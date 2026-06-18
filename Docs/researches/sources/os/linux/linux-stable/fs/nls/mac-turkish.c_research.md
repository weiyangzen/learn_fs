# File Research: sources/os/linux/linux-stable/fs/nls/mac-turkish.c

This file implements the Linux NLS module for Macintosh Turkish, registered as `macturkish`.

The generated mapping is based on Mac Roman with Turkish-specific assignments. `charset2uni[256]` maps high bytes to Western European characters plus Turkish letters such as `U+011E/U+011F`, `U+0130/U+0131`, and `U+015E/U+015F`. It also contains the Apple private-use mapping `0xf0 -> 0xf8ff` and a Turkish-specific private-use value `0xf5 -> 0xf8a0`. Reverse lookup uses `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`.

The operational code is the shared NLS generated skeleton. `uni2char()` maps Unicode back to one byte through sparse pages and enforces output capacity. `char2uni()` maps one byte to Unicode and rejects null mappings. The `nls_table` binds `.charset = "macturkish"`, the callbacks, and static case arrays.

The reverse mapping includes Turkish letters in `page01` and the private-use `pagef8` entry, making it different from the base Mac Roman table even though much of the punctuation and Latin mapping is shared. As with the other Mac generated modules here, `charset2lower` and `charset2upper` are filled with `0xff`, so Turkish dotted/dotless-I case behavior is not implemented by these tables.

The file registers/unregisters through the kernel NLS registry and declares `MODULE_DESCRIPTION("NLS Codepage macturkish")`, `Dual BSD/GPL`, and the Unicode data permission notice.
