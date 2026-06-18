# File Research: sources/virtualization/nbdkit/filters/blocksize/Makefile.am

Purpose: builds the `nbdkit-blocksize-filter.la` module and optional man page.

Key details:
- Sources are `blocksize.c` and `include/nbdkit-filter.h`.
- Includes nbdkit headers, generated headers, `common/include`, and `common/utils`.
- Links utility, replacement compatibility, and Windows import libraries.
- Applies the shared filter symbol version script when configured.
- Generates `nbdkit-blocksize-filter.1` from POD under `HAVE_POD`.

Integration notes:
- This build mirrors the blocksize-policy filter but compiles the transforming blocksize implementation rather than just policy enforcement.
