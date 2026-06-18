## sources/test-tools/syzkaller/pkg/kfuzztest/extractor.go

Purpose: extracts KFuzzTest metadata from a `vmlinux` ELF/DWARF image.

Important APIs/types/functions: `Extractor`, `NewExtractor`, `ExtractAllResult`, `ExtractAll`, `Close`, `String`, `elfSection`, `readElfString`, `buildSymbolIndex`, `getSymbol`, `extractFuncs`, `extractDomainConstraints`, `extractAnnotations`, `dwarfGetType`, `extractStructs`, and generic `parseKftfObjects`.

Control flow: opens ELF and DWARF, lazily indexes symbols, parses dense records between start/end symbols for targets/constraints/annotations, reads pointed-to strings, then scans DWARF struct entries matching target input types and recursively visits nested structs through fields/pointers/qualifiers. `ExtractAll` enforces consistency between funcs and structs.

State and persistence: holds open ELF file and DWARF data until `Close`; caches symbol map.

Dependencies and integration: depends on metadata record layouts from `types.go`, ELF section/symbol tables, DWARF debug info, and builder input types.

Risks: requires unstripped vmlinux with expected linker symbols and DWARF. `readElfString` limits strings to 128 bytes. Struct recursion uses struct names as visited keys, so anonymous/duplicate names can be problematic. Missing start/end symbols are hard errors even when a section is empty.

Test signals: description generation tests exercise extraction from fixture binaries.
