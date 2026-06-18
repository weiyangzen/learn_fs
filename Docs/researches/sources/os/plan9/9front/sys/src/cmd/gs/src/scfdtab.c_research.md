# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfdtab.c

Generated CCITTFaxDecode table source. It defines `cf_white_decode`, `cf_black_decode`, `cf_2d_decode`, and `cf_uncompressed_decode` arrays of `cfd_node` entries consumed by `scfd.c`.

The arrays encode run lengths, exceptional values such as EOL/invalid/uncompressed/pass/horizontal, and code lengths. They are generated from the encoder-side canonical tables and the generator logic in `scfdgen.c`.

Dependencies include `scommon.h` and `scf.h`. The dummy `scfdtab_dummy` exists for old compilers.

This is generated compression metadata, not executable algorithm logic beyond table storage.
