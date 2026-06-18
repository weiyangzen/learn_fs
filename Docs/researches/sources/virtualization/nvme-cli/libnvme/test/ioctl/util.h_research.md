# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/util.h

## Role

`util.h` declares the ioctl test helper API and defines assertion and cleanup convenience macros.

## API

It declares `fail()`, `cmp()`, `arbitrary()`, and `arbitrary_range()`. The `check(condition, fmt...)` macro aborts via `fail()` when a condition is false.

It also defines `__cleanup(fn)`, `freep()`, and `__cleanup_free`, enabling GNU cleanup-based automatic freeing in the tests.

## Filesystem/Storage Relevance

This is local test scaffolding for storage command validation.
