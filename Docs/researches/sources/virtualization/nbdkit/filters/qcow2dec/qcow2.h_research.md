# File Research: sources/virtualization/nbdkit/filters/qcow2dec/qcow2.h

This internal header defines the packed qcow2 header layout used by `qcow2dec.c`, including v2 fields, v3 feature fields, and `compression_type`. It also defines the qcow2 magic string and bit numbers for known incompatible, compatible, and autoclear feature flags.

The header provides masks for validating/extracting L1 and L2 entries, including reserved-bit masks, offset masks, and the L2 compressed-cluster type bit. It is intentionally narrow and models only the qcow2 metadata needed by the decoder filter.
