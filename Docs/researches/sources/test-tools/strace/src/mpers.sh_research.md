<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mpers.sh -->
# sources/test-tools/strace/src/mpers.sh

Purpose: builds mpers type headers for parser files that declare `DEF_MPERS_TYPE`.
Important APIs/types/functions: shell pipeline using `sed`, `CPP`, `CC`, `READELF`, `gawk -f mpers.awk`, `ARCH_FLAG`, `CC_ARCH_FLAG`, and generated `mpers-$ARCH/type.h` files.
Control flow: extracts target mpers types, synthesizes small C files, preprocesses dependency visibility, compiles with DWARF, normalizes readelf output, and runs the awk generator for each type.
State and persistence behavior: writes generated/intermediate files under `mpers-$ARCH_FLAG`. Dependencies and integration points: build system, compiler, readelf, gawk, parser sources.
Risks: shell quoting, tool version differences, and DWARF output changes can break generation. Test signals: run `mpers_test.sh` and full cross-personality build.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mpers.sh -->
