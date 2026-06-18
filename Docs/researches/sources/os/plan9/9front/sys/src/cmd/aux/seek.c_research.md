# File Research: sources/os/plan9/9front/sys/src/cmd/aux/seek.c

`seek` benchmarks random 512-byte reads from a block device or file. It opens the argument read-only, computes sector count from file size, performs 100 random sector `pread`s, and prints elapsed time divided by `100000000`, effectively seconds per ten reads scale.

It is a simple latency probe for `/dev/sd??/data`-style devices and exits on any short read.
