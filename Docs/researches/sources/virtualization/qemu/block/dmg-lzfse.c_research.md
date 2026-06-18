# File Research: sources/virtualization/qemu/block/dmg-lzfse.c

Optional DMG LZFSE decompression module. It includes the LZFSE header with a diagnostic workaround for strict-prototypes warnings, then defines `dmg_uncompress_lzfse_do()` using `lzfse_decode_buffer()`.

Unlike the bzip2 helper, it returns the decoded output size on success and `-1` on failure. A constructor registers the helper through the global `dmg_uncompress_lzfse` function pointer. The main DMG driver detects whether this optional module is available before treating ULFO chunks as readable.
