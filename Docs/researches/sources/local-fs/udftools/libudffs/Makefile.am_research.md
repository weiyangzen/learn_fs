# File Research: sources/local-fs/udftools/libudffs/Makefile.am

Builds internal Libtool library `libudffs.la`.

Sources:
- `crc.c`
- `extent.c`
- `misc.c`
- `unicode.c`
- shared headers from `../include`

Links `@LTLIBOBJS@` and uses `-I$(top_srcdir)/include`.

Key role: shared non-installed library for UDF CRCs, extent planning, encoding, and miscellaneous helpers.
