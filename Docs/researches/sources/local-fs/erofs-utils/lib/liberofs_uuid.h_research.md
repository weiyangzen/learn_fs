# File Research: sources/local-fs/erofs-utils/lib/liberofs_uuid.h

This header declares UUID helper functions:
- `erofs_uuid_generate(unsigned char *out)`
- `erofs_uuid_unparse_lower(const unsigned char *buf, char *out)`
- `erofs_uuid_parse(const char *in, unsigned char *uu)`

Known user in this group:
- `rebuild.c` uses `erofs_uuid_unparse_lower()` to produce a fallback filesystem identifier when a source sb has no `devname`.

Output sizing:
- `erofs_uuid_unparse_lower()` callers should provide space for canonical UUID text plus NUL; `rebuild.c` uses a 37-byte buffer.
