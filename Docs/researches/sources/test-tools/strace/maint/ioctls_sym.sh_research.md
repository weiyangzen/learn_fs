# sources/test-tools/strace/maint/ioctls_sym.sh

Purpose: discovers ioctl macros defined through `_IO`, `_IOR`, `_IOW`, `_IOWR`, and related symbolic forms by preprocessing and compiling candidate Linux headers, then extracting encoded values from DWARF.

Important APIs/types/functions: candidate header discovery via `find`/`grep`, temp include overrides for `asm/ioctl.h`, `process_file`, generated `printents.c`, many header-specific workaround cases, `CPP`, `CC`, `READELF`, `fixes.h`, `defs.h`, and `ioctls_sym.awk`.

Control flow: find headers containing ioctl-like macro patterns, set up a temporary include tree redefining `_IOC` to encode fields as array sizes, then process each header in a subshell. For each file, generate compatibility includes/workarounds, possibly rewrite or filter header content, preprocess with `-dD`, extract locally defined ioctl names, create declarations `struct {NAME;} ioc_NAME;`, compile with DWARF, dump debug info, normalize it, run awk, and output entries.

State and persistence behavior: uses a temp directory removed on exit. Emits ioctl entries to stdout and progress/failure messages to stderr. Environment variables can override compiler/preprocessor/readelf and flags.

Dependencies and integration points: called by `ioctls_gen.sh`; depends heavily on Linux UAPI header layout and compiler/debug-info behavior. Supports prefixing header names for Android staging.

Risks: large maintenance surface of fragile per-header workarounds. Build failures for one header are counted but do not abort the whole run. Host architecture affects KVM and other filtering. DWARF format/compiler changes can break extraction.

Test signals: processing a Linux header tree should finish with low/no failed files and produce stable sorted ioctl entries that compile into strace's ioctl lookup tables.
