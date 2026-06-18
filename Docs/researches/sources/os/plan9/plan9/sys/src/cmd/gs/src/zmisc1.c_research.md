# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc1.c

Miscellaneous Type 1 font encryption operators and eexec filters. It registers `.type1encrypt`, `.type1decrypt`, `eexecEncode`, and `eexecDecode`.

`type1crypt` is the shared implementation for `.type1encrypt` and `.type1decrypt`: it takes input string, seed, and output string, checks output capacity, applies the supplied Type 1 crypt routine, updates the seed, and returns the output substring and new seed. `ztype1encrypt` and `ztype1decrypt` select encrypt/decrypt callbacks from `gscrypt1.h`.

`eexec_param` extracts optional `seed` from a parameter dictionary or defaults it. `zexE` and `zexD` create eexec encode/decode filters through the stream filter framework. The file is small but important for Type 1 font program handling.
