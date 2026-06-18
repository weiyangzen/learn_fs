# File Research: sources/os/bsd/netbsd-src/lib/libpam/Makefile.inc

Shared PAM build settings. It enables fortification by default for authentication/network-client code, sets the module directory under `/usr/lib[/<mlib>]/security`, defines `OPENPAM_MODULES_DIRECTORY`, and controls static-vs-shared module compilation with `OPENPAM_STATIC_MODULES`.

It defines the shared major version as 4 for libpam and modules, and requires installed files to be owned by root.
