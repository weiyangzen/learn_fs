# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzassert.c

libbzip2 assertion failure handler.

Defines `BZ2_bz__AssertH__fail(int errcode)`, which prints a detailed internal-error message including the libbzip2 version and exits with status 3.

This is the hard assertion path used by `AssertH` in the bzip2 internals, including block sorting and decompression.
