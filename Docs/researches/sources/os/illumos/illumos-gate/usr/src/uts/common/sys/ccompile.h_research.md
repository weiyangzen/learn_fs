# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ccompile.h

`ccompile.h` centralizes compiler feature and attribute macros. It computes `__GNUC_VERSION`, defines printf/kprintf format checking attributes, `format_arg`, noreturn, GNU inline behavior, returns-twice, pure/const, alignment, unused, sentinel, used, weak, hidden visibility, cache-line alignment, packed/section, and `__nonstring`.

The header smooths differences between GCC, lint/Sun-style attributes, debug vs release unused-variable handling, and feature tests such as `__has_attribute`.
