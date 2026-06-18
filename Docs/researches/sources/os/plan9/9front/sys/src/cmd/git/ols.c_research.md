# File Research: sources/os/plan9/9front/sys/src/cmd/git/ols.c

Object-list iterator over `.git/objects`. It first enumerates loose objects under two-hex-character directories, then packed objects by reading `.idx` files in `.git/objects/pack`.

`mkols` snapshots top-level and pack directories, `olsnext` advances through loose then packed stages, and `olsfree` releases open descriptors and directory arrays. Packed enumeration reads the fanout count from the index and then sequentially reads stored object hashes.
