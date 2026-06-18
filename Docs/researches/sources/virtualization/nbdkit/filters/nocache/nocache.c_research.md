# File Research: sources/virtualization/nbdkit/filters/nocache/nocache.c

This filter changes how the server advertises and handles `NBD_CMD_CACHE`. The `cache-mode` / `cachemode` parameter accepts `none` (default), `emulate`, and `nop` / `no-op`.

`nocache_can_cache` maps those modes to `NBDKIT_CACHE_NONE`, `NBDKIT_CACHE_EMULATE`, or `NBDKIT_CACHE_NATIVE`. In `NOP` mode the filter advertises native cache support but implements `.cache` as a no-op that returns success, requiring zero flags and asserting that the mode is active.

The filter has intentionally narrow behavior: it does not pass cache requests to the backend, and it does not alter ordinary reads or writes. Its main risk is semantic: `nop` can make clients believe cache hints are honored even though they are intentionally ignored.
