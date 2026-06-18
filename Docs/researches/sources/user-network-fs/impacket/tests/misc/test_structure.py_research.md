# sources/user-network-fs/impacket/tests/misc/test_structure.py

Purpose: Regression-tests Impacket's generic `Structure` binary packing/unpacking DSL across strings, arrays, alignment, nested structures, optional pointers, computed fields, and error reporting.

Important APIs, types, and functions: Uses `impacket.structure.Structure`, shared `_StructureTest`, `hexl`, and multiple inline `Structure` subclasses with format codes such as `z`, `u`, `w`, `:`, `B*<L`, `_`, length expressions, optional pointer syntax, and alignment.

Control flow: Shared tests populate structures, serialize, compare expected hex, reparse, and reserialize. Specialized tests cover bogus length failure, aligned packing, UTF-16 embedded NUL handling, nested structures, optional sparse pointers, ASCII-Z arrays, unpack-code fields, clear errors for missing NUL terminators, and computed bitfield decomposition.

State and persistence behavior: Pure in-memory serialization tests.

Dependencies and integration points: `Structure` underpins many Impacket protocol parsers, so this suite protects broad binary parsing behavior.

Risks: Format-expression evaluation and alignment changes have wide blast radius. Exact byte assertions are deliberately brittle to catch layout changes.

Test signals: Strong signal for round-trip stability, alignment, pointer optionality, string termination errors, nested packing, computed fields, and field-name-rich exceptions.
