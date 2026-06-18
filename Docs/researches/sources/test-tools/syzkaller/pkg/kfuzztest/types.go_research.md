## sources/test-tools/syzkaller/pkg/kfuzztest/types.go

Purpose: binary parsers for fixed-size KFuzzTest ELF metadata records.

Important APIs/types/functions: `parsableFromBytes`, `kfuzztestTarget`, `kfuzztestConstraint`, `kfuzztestAnnotation`, size/start/end constants, `incorrectByteSizeErr`, and each record’s `fromBytes/size/startSymbol/endSymbol`.

Control flow: each parser validates byte length, reads fields with ELF byte order, truncates enum fields to low byte, and exposes section boundary symbol names for generic extraction.

State and persistence: no state; parses bytes from ELF sections.

Dependencies and integration: used by `parseKftfObjects` in `extractor.go`; must match C/kernel metadata layout.

Risks: parser assumes 64-bit pointer-sized fields and fixed alignment. `uintptr` conversion can truncate on 32-bit hosts, though KFuzzTest manager targets Linux/AMD64.

Test signals: exercised through compiled C fixtures.
