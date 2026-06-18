# sources/test-tools/ltp/testcases/kernel/fs/doio/open_flags.c

Purpose: converts symbolic `open(2)` flag lists to integer bitmasks and converts bitmasks back to symbolic text for diagnostics in the doio tools.

Important APIs/types/functions: `parse_open_flags`, `openflags2symbols`, static `Open_flags[]`, static return buffer `Open_symbols`, `UNKNOWN_SYMBOL`, and optional `UNIT_TEST` main. The table conditionally includes platform flags such as `O_DIRECT`, `O_LARGEFILE`, `O_RAW`, `O_SSD`, `O_PARALLEL`, and legacy SGI/Cray values when available.

Control flow: `parse_open_flags` walks comma-separated tokens in place, temporarily null-terminates each token, searches `Open_flags`, ORs matched bits, restores the separator, and returns `-1` plus the bad token pointer on an unknown symbol. `openflags2symbols` handles the implicit `O_RDONLY` case, consumes matching bits from the bitmask, joins names with the caller separator, and optionally appends `UNKNOWN`.

State/persistence behavior: no filesystem state is changed. The conversion-to-string path writes a process-global static buffer, so the result is overwritten by subsequent calls and is not thread-safe.

Dependencies/integration: used by `iogen` option parsing and by doio diagnostics that need readable open flags. It depends on `<fcntl.h>` feature macros so the symbol table varies by target platform.

Risks/test signals: adding new kernel open flags without updating this table yields `UNKNOWN` output or parse failures. `parse_open_flags` mutates the input buffer while parsing, even though it restores separators. Optional unit testing accepts either numeric bitmasks or symbolic lists and prints the conversion result.
