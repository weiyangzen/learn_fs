# File Research: sources/local-fs/erofs-utils/lib/remotes/oci.c

This file implements OCI/Docker registry import and OCI blob-backed virtual I/O. When `OCIEROFS_ENABLED` is not defined, `ocierofs_io_open()` returns `-EOPNOTSUPP`; the full implementation requires curl and json-c feature support.

Registry/auth flow:
- `ocierofs_parse_ref()` parses image references, defaulting Docker Hub to `registry-1.docker.io`, `library/<name>`, and `latest`.
- `ocierofs_get_platform_spec()` maps host OS/architecture to OCI platform strings.
- `ocierofs_prepare_auth()` tries bearer-token auth and falls back to basic auth when credentials exist.
- `ocierofs_get_auth_token()` handles Docker Hub, discovered `WWW-Authenticate` realms, and several fallback auth endpoint patterns.
- Docker config credentials are loaded through `erofs_docker_config_lookup()` when CLI credentials are absent.

Manifest/layer selection:
- `ocierofs_get_manifest_digest()` fetches a manifest or manifest list/index, selects a platform-specific manifest, or treats the tag as manifest digest when appropriate.
- `ocierofs_fetch_layers_info()` loads layer digest, media type, and size from the selected manifest.
- `ocierofs_prepare_layers()` validates requested layer index or blob digest and fills `ctx->blob_digest` when needed.

Full import path:
- `ocierofs_extract_layer()` downloads a layer blob into a temp file.
- `ocierofs_process_tar_stream()` opens the layer as a tar stream. It uses gzip by default, raw tar for tarindex-only, and GZRAN when both tarindex and zinfo are configured. It repeatedly calls `tarerofs_parse_tar()` until archive end and exports zinfo when applicable.
- `ocierofs_build_trees()` initializes context, selects all layers or one selected layer, rejects tarindex mode unless exactly one layer is selected, downloads/processes each layer, and records tar-offset-derived device blocks for tarindex mode.

Range I/O path:
- `ocierofs_download_blob_range()` issues HTTP `Range` requests for the selected blob, handling `206` and some `200` fallback behavior.
- `ocierofs_io_pread()` and `ocierofs_io_read()` expose the selected remote blob as an `erofs_vfile`.
- `ocierofs_io_open()` allocates context and iostream state, requires `blob_digest`, and installs `ocierofs_io_vfops`.
- `ocierofs_io_close()` cleans up context and stream.

Credential helpers:
- `ocierofs_encode_userpass()` base64-encodes `username:password`.
- `ocierofs_decode_userpass()` decodes and splits the same format.

Built-in tests:
- Under `OCIEROFS_ENABLED && TEST`, there is a parse-reference test harness covering Docker Hub defaults, custom registries, ports, nested repositories, and tags.

Risks / notes:
- `ocierofs_extract_layer()` returns a temp fd directly on success; caller closes it after tar processing.
- Range fallback for `HTTP 200` copies from a full response when offset is nonzero, which can be expensive for registries that ignore range requests.
- Auth header parsing is simple string scanning and may not cover all valid quoted/auth parameter edge cases.
