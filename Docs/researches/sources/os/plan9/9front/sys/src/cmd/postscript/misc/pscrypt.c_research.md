# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/misc/pscrypt.c

`pscrypt.c` implements Adobe Type 1 eexec/CharString encryption and decryption. It supports binary or hex input/output, explicit encrypt/decrypt mode, custom seed/key, output offset control, and hex line length.

The core loop applies the standard rolling key update with constants 52845 and 22719, omitting or adding the initial random/key bytes according to mode defaults.
