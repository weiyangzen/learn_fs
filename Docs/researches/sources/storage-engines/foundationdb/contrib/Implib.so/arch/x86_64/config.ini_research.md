# sources/storage-engines/foundationdb/contrib/Implib.so/arch/x86_64/config.ini

## Purpose
Architecture metadata for the POSIX import-library generator on x86_64.

## Important APIs, Types, and Functions
Defines 8-byte pointer size and relocation type `R_X86_64_64`.

## Control Flow and Integration
`implib-gen.py` reads this when target architecture is x86_64 and uses it while reconstructing relocated data/vtable definitions.

## State and Persistence
Depends on readelf relocation names for x86_64 ELF.

## Dependencies
No dynamic state; static config file.

## Risks and Test Signals
Risks include not handling relative or GOT relocation forms for all exported data cases. Test signal is wrapper generation for x86_64 shared libraries.
