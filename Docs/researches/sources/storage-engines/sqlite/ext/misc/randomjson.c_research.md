# sources/storage-engines/sqlite/ext/misc/randomjson.c

Purpose: registers deterministic `random_json(seed)` and `random_json5(seed)` functions for parser/test corpus generation.

Important APIs/types/functions: `Prng`, `prngSeed()`, `prngInt()`, `azJsonAtoms[]`, `azJsonTemplate[]`, `jsonExpand()`, and `randJsonFunc()`. `sqlite3_randomjson_init()` registers JSON and JSON5 variants.

Control flow: seed local PRNG state, expand `%` placeholders through several template passes, replace `XX`/`DD` markers with generated hex/digits, then return capped text from fixed 10 KB buffers.

State and persistence: no persistent state; output is deterministic for seed and mode.

Dependencies/integration: SQLite scalar function API and JSON/JSON5 test use cases.

Risks/test signals: buffer truncation can affect validity, sequence changes break fixtures, and generated values intentionally include edge atoms such as Infinity/NaN for JSON5. Test stable output by seed, parser validity where expected, placeholder exhaustion, size cap behavior, and diversity of generated arrays/objects/scalars.
