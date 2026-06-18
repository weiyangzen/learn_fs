# File Research: sources/local-fs/ntfs-3g/ntfsprogs/boot.h

Small guarded header declaring `extern const unsigned char boot_array[4136];`.

It exposes the mkntfs boot-code template from `boot.c`. The key invariant is declaration-size agreement with `BOOTCODE_SIZE` and the actual array definition.
