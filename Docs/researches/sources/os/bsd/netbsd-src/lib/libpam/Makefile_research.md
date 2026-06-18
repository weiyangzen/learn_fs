# File Research: sources/os/bsd/netbsd-src/lib/libpam/Makefile

Top-level PAM build ordering file. It builds `staticmodules`, waits, builds `libpam`, waits, then builds dynamic `modules`.

This ordering is required because static modules are linked into static `libpam.a`, while dynamic modules depend on the shared libpam.
