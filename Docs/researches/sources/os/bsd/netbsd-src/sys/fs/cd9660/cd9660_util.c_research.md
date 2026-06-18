# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_util.c

Read completely: 260 lines.

Provides filename character handling for ISO9660 and Joliet. The global `cd9660_utf8_joliet` controls whether Joliet UCS-2 names are exposed as UTF-8 or reduced to an ISO-8859-1-like byte subset with nonrepresentable high-byte characters replaced by `?`.

`isochar()` decodes one on-disc ISO/Joliet filename character. `isofncmp()` compares a caller-supplied name against an ISO directory name, allowing omitted `;version` suffixes and doing ASCII case folding for ordinary ISO names. `isofntrans()` translates on-disc names to exported names, optionally preserving original `;version`, lowercasing, adding the associated-file `=` prefix, and stopping at version separators.

The internal `wget()` and `wput()` bridge caller names to/from UTF-8 for Joliet via `<fs/unicode.h>`. The file is usable in kernel and selected tool builds, with userland includes guarded for `macppc_installboot`.
