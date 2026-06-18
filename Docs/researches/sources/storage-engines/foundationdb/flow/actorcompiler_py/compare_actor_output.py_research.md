## sources/storage-engines/foundationdb/flow/actorcompiler_py/compare_actor_output.py

Purpose: this utility compares two generated actor compiler outputs, allowing path differences inside `#line` directives so C# and Python compiler outputs can be checked for semantic/textual parity.

Important APIs: `compare_outputs(file1_path, file2_path)` reads both files, returns true for exact equality, normalizes quoted filenames in `#line <number> "path"` directives to `NORMALIZED_PATH`, compares again, and prints a unified diff of normalized content on mismatch. `main()` parses two path arguments and exits nonzero if comparison fails.

Control flow: exact compare first, normalized compare second, diff/false on mismatch, exception/false on read or comparison errors.

State and persistence behavior: read-only utility; it writes only diagnostics to stderr.

Dependencies and integration points: uses `argparse`, `pathlib`, `re`, `difflib`, and `sys`. It is a migration/test helper for proving the Python actor compiler matches the existing generated output apart from source path differences.

Risks: normalization is intentionally narrow; differences in line numbers, whitespace, generated identifiers, or UID output still fail. It compares one file pair and does not handle UID sidecars unless explicitly passed as inputs. The regex only normalizes `#line` directives with quoted paths.

Test signals: unit tests should cover exact match, path-only line-directive differences, real content differences with diff output, missing files, and generated actor outputs from both compilers.
