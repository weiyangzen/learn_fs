# File Research: sources/local-fs/erofs-utils/lib/liberofs_oci.h

This header declares OCI image import and OCI-backed vfile support.

Configuration:
- `struct ocierofs_config` includes image reference, platform, optional credentials, optional blob digest or layer index, tarindex/zinfo paths, and insecure transport flag.

Runtime types:
- `struct ocierofs_layer_info` stores digest, media type, and size.
- `struct ocierofs_ctx` stores curl handle, auth header, registry/repository/platform/tag/manifest, layer list, blob selection, and scheme.
- `struct ocierofs_iostream` stores context and sequential read offset for HTTP range-backed vfiles.

API:
- `ocierofs_build_trees()` downloads selected image layers, parses tar content, and populates an importer.
- `ocierofs_io_open()` opens a range-read vfile for a selected blob.
- `ocierofs_encode_userpass()` / `ocierofs_decode_userpass()` handle base64 username/password strings.
- `ocierofs_get_platform_spec()` returns host platform in OCI `os/arch[/variant]` form.

Known implementation:
- `remotes/oci.c`.

Risk / note:
- The same context type supports both full layer import and random-access layer I/O, so cleanup ownership is important: `ocierofs_io_close()` owns and frees the heap context created by `ocierofs_io_open()`.
