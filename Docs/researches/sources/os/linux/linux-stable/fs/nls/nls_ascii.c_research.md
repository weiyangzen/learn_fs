# File Research: sources/os/linux/linux-stable/fs/nls/nls_ascii.c

This file implements the minimal Linux NLS module for ASCII, registered as charset `ascii`.

The module contains a 128-entry `charset2uni` table for `0x00` through `0x7f`, a `page00` reverse table for Unicode page 0, and ASCII case-conversion tables. Unlike the Mac generated modules in this group, `charset2lower` and `charset2upper` contain real ASCII folding for `A-Z` and `a-z`.

The conversion callbacks are simple:
- `uni2char()` indexes `page_uni2charset` by the high Unicode byte and returns a one-byte ASCII value only if the reverse table entry is nonzero.
- `char2uni()` maps the input byte through `charset2uni`; because the table only has explicit data for ASCII range, high-byte use would be outside the intended charset contract.
- Both callbacks reject `0x0000` as an ordinary character because zero table entries are used as “unmapped.”

`struct nls_table table` wires the charset name, conversion callbacks, and case maps. `init_nls_ascii()` registers the table; `exit_nls_ascii()` unregisters it. Module metadata declares `NLS ASCII (United States)` and `Dual BSD/GPL`.

This file is the straightforward single-byte baseline used when filesystems request ASCII-only name conversion.
