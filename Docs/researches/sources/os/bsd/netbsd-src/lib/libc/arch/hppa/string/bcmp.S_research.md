# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/bcmp.S

This HPPA `bcmp` routine compares two byte streams one byte at a time using post-increment loads. It exits on mismatch or count exhaustion and returns the byte difference in `%ret0`, with zero meaning equality.
