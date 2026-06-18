# File Research: sources/os/bsd/netbsd-src/lib/librefuse/fuse_opt.h

This public option-parsing header defines FUSE option keys, `struct fuse_opt`, helper macros, the option callback type, and APIs for adding/copying/freeing/inserting args, composing `-o` option strings, parsing options, and matching templates.

Integration points: implemented by `refuse_opt.c`, consumed by command-line setup, mount compatibility wrappers, and librefuse's own `debug`/`fsname` options. Risks are template matching compatibility with libfuse and ownership rules for allocated argument vectors and `%s` destinations.
