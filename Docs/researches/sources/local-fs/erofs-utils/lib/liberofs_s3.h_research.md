# File Research: sources/local-fs/erofs-utils/lib/liberofs_s3.h

This header declares S3 remote import support.

Enums:
- `s3erofs_url_style`: path style or virtual-host style.
- `s3erofs_signature_version`: AWS Signature Version 2 or Version 4.

Constants:
- Access key and secret key buffers are 256 bytes plus NUL.

Configuration/runtime:
- `struct erofs_s3` stores a curl handle, endpoint, region, credentials, URL style, and signature version.

API:
- `s3erofs_build_trees(struct erofs_importer *im, struct erofs_s3 *s3, const char *path, bool fillzero)`

Known implementation:
- `remotes/s3.c`.

Behavior from implementation:
- Lists objects from an S3 bucket/prefix, creates corresponding in-memory EROFS dentries/inodes, and either downloads object contents or fills files with zeroes.
