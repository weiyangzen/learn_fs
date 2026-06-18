# sources/storage-engines/foundationdb/contrib/Implib.so/arch/aarch64/config.ini

## Purpose
Architecture metadata for the POSIX import-library generator on aarch64.

## Important APIs, Types, and Functions
Defines `PointerSize = 8` and `SymbolReloc = R_AARCH64_ABS64` in an `[Arch]` section.

## Control Flow and Integration
`implib-gen.py` selects this file when the target triple starts with aarch64/armv8 and uses it to parse relocated vtable/data entries.

## State and Persistence
Depends on GNU readelf relocation type names matching `R_AARCH64_ABS64`.

## Dependencies
No dynamic state; static config file.

## Risks and Test Signals
Risks include incomplete relocation coverage for more complex aarch64 shared objects. Test signal is generated trampolines/import wrapper for an aarch64 ELF library.
