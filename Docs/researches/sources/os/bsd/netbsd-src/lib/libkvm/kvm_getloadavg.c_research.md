# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_getloadavg.c

Implements `kvm_getloadavg()`. For live kernels, it delegates directly to `getloadavg()`. For dead kernels, it resolves `_averunnable` and optional `_fscale`, reads `struct loadavg` from the dump, and converts fixed-point load averages to doubles.

It preserves compatibility with old kernels where `fscale` was a separate symbol.
