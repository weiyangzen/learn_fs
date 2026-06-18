# File Research: sources/os/plan9/9front/sys/src/cmd/aux/txt2uimage.c

`txt2uimage` wraps a file or stdin into a U-Boot image with an 8-byte script payload prefix. It writes a 64-byte U-Boot header, data length and zero word, original data, then computes and fills data CRC and header CRC.

The image type is `IH_TYPE_SCRIPT`, compression is none, load/entry are zero, and the output defaults to `<input-name>.u` unless `-o` is supplied. It rejects files larger than 32-bit size minus prefix.

Caveat: `copy` uses `i = n & sizeof(buf) - 1`, which depends on C precedence and likely does not mean `n & (sizeof(buf)-1)` unless parsed as intended by the compiler.
