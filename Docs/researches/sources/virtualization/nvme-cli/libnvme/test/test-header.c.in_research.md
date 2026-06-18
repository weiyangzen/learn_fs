# File Research: sources/virtualization/nvme-cli/libnvme/test/test-header.c.in

## Role

`test-header.c.in` is a template used to generate one compile test per public libnvme header.

## Behavior

Meson substitutes `@HDR@` and generates a C file that includes `<nvme/@HDR@.h>` as the first and only header, then defines an empty `main()` returning zero.

The purpose is to ensure every public header is self-sufficient and does not require prior includes.

## Dependencies

- Meson configuration substitution.
- Public libnvme header installation layout.

## Filesystem/Storage Relevance

No direct storage behavior. It protects consumers of libnvme storage APIs from header dependency bugs.
