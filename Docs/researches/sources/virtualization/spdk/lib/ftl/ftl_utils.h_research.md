# File Research: sources/virtualization/spdk/lib/ftl/ftl_utils.h

Small umbrella header for common FTL utility headers:
- `utils/ftl_defs.h`
- `utils/ftl_mempool.h`
- `utils/ftl_conf.h`
- `utils/ftl_md.h`
- `utils/ftl_property.h`

It has no logic of its own. Its role is convenience inclusion for modules that need the common definitions, memory pool, configuration, metadata, and property helpers.
