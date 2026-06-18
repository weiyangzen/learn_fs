# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/Makefile.in

## Purpose
`lib/uuid/Makefile.in` builds, installs, documents, and tests the e2fsprogs libuuid implementation.

## Important APIs, Types, and Functions
It defines object/source lists for clear, compare, copy, generate, parse, pack/unpack, unparse, and uuid_time; shared-library metadata; manpage substitution targets; generated `uuid.h`, `uuid_types.h`, `uuid.pc`; and test utilities `tst_uuid` and `uuid_time`.

## Control Flow
The build generates headers and manpages through configure substitution, compiles library variants, links test/debug utilities, installs headers, library, manpages, symlinked manpage aliases, and pkg-config metadata. `check` runs `tst_uuid`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is generated headers/docs, archives/shared images, and test binaries. Dependencies include top-level make fragments, `config.status`, substitution helpers, and optional platform features used by `gen_uuid.c`. Risks include generated header ordering, installed manpage symlink behavior, and ABI version settings. Test signal is successful `tst_uuid`.
