<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/parse-types.sh -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/parse-types.sh

Source read: complete file, 118 lines, 2346 bytes, sha256 `5dec511c9bba0b707794f7c88776e45571fa9ec96849b84dd19dfb28f68a0b81`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/parse-types.sh_research.md`.

Purpose: configure-time helper that derives Linux `__u*` and `__s*` typedef backing types from `<asm/types.h>`, validates their byte widths, and writes `asm_types.h` for later substitution into generated e2fsprogs headers.

Important APIs/types/functions: builds a temporary `sed.script` that strips comments/blanks and converts typedefs such as `typedef unsigned int __u32;` into `#define __U32_TYPEDEF unsigned int`. Uses `CC`, `CPP`, and `BUILD_CC` environment variables, defaulting to gcc-style commands. Generates and compiles `asm_types.c` to validate 8/16/32/64-bit signed and unsigned widths.

Control flow: writes sed script; preprocesses an include of `<asm/types.h>`; filters macro definitions into `asm_types.h`; removes sed script; copies `asm_types.h` to a C source; appends a test program checking each discovered typedef with `sizeof`; compiles and executes the test; preserves `asm_types.h` on success or empties it on validation failure; removes temporary C and executable files.

State and persistence behavior: persistent output is `asm_types.h` in the current directory. Temporary files are `sed.script`, `asm_types.c`, and `asm_types`, all removed on the normal path.

Dependencies and integration: used by `Makefile.in` rules that generate `lib/ext2fs/ext2_types.h`, `lib/blkid/blkid_types.h`, and `lib/uuid/uuid_types.h`. Depends on a compiler/preprocessor, Linux-like `asm/types.h`, `sed`, `grep`, `cp`, and executable build host.

Risks: assumes preprocessed typedef format matches the sed expressions; cross-compilation can fail because it runs the built `asm_types` executable on the build host; uses old-style C `main()` without an explicit return type; warning directives may be compiler-specific. On validation failure it silently leaves an empty `asm_types.h`, which can move failure later into header generation.

Test signals: run during configure/build on target environments and confirm non-empty `asm_types.h` with all expected typedef defines. Cross-build tests should verify `BUILD_CC` is set correctly and that generated ext2/blkid/uuid type headers compile.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/parse-types.sh -->
