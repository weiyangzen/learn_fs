# sources/test-tools/kdevops/scripts/mirror-docker-images.sh

## Purpose
Mirrors Docker images used by kdevops workflows into a local registry and optionally stores compressed offline archives.

## Important APIs
Functions include `check_registry()`, `mirror_image(image)`, `save_image_archive(image)`, `load_images_list(file)`, `scan_for_images()`, `create_manifest()`, `main()`, and `show_usage()`. Environment knobs are `MIRROR_DIR` and `REGISTRY_PORT`; positional argument 1 may be an image-list file.

## Control flow
The script validates that `http://localhost:$REGISTRY_PORT/v2/` responds, creates `$MIRROR_DIR/images/manifest.txt`, appends custom images, optionally scans role defaults for image references, then loops over `DEFAULT_IMAGES`. Each image is pulled, retagged as `localhost:$REGISTRY_PORT/<image_name>`, pushed, and optionally archived with `docker save`, `gzip`, and `sha256sum`.

## State and persistence
Persists a manifest under `$MIRROR_DIR/images/manifest.txt` and archives under `$MIRROR_DIR/images/archives`. Docker daemon image/tag state is modified.

## Dependencies and integration
Requires `docker`, `curl`, `gzip`, `sha256sum`, and a running registry. It supports mirror setup for vLLM, MinIO, Milvus, LMCache, etcd, and registry images.

## Risks and test signals
Tag rewriting uses `${image#*/}`, which can collapse registry namespaces and may collide for images sharing the same tail. `--scan` is only checked in `$2`, so option ordering is limited. Test by running with a small custom list against a local registry and checking manifest entries, pushed tags, and archive checksums.
