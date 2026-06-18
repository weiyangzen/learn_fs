# File Research: sources/local-fs/erofs-utils/lib/liberofs_gzran.h

This header declares gzip random-access index builder/open support.

Constant:
- `EROFS_GZRAN_WINSIZE` is 32768 bytes, matching gzip/deflate window size.

Types:
- Opaque `struct erofs_gzran_builder`.

Builder API:
- `erofs_gzran_builder_init(struct erofs_vfile *vf, u32 span_size)`
- `erofs_gzran_builder_read(struct erofs_gzran_builder *gb, char *window)`
- `erofs_gzran_builder_export_zinfo(struct erofs_gzran_builder *gb, struct erofs_vfile *zinfo_vf)`
- `erofs_gzran_builder_final(struct erofs_gzran_builder *gb)`

Reader API:
- `erofs_gzran_zinfo_open(struct erofs_vfile *vin, void *zinfo_buf, unsigned int len)`

Known users:
- `remotes/oci.c` selects the GZRAN decoder when tarindex and zinfo paths are provided, then exports zinfo after processing.

Risk / note:
- This is a stream/index integration point: caller-owned vfiles and zinfo buffers must remain valid for the opened reader/builder lifetime.
