# sources/storage-engines/rocksdb/build_tools/amalgamate.py research

Purpose: `amalgamate.py` converts a RocksDB unity-build source into an amalgamated C++ source and header. It recursively expands quoted `#include` directives, sending public headers to the generated header and private headers/source content to the generated source.

Important APIs: `find_header(name, abs_path, include_paths)` resolves includes relative to the current file first and then configured include paths. `expand_include()` guards against repeated expansion with the global `included` set and calls `process_file()`. `process_file()` is the recursive include expander. `main()` defines CLI arguments for source, private include paths `-I`, public include paths `-i`, excluded headers `-x`, source output `-o`, and header output `-H`.

Control flow: `main()` normalizes paths, seeds the global `excluded` set, opens output files, writes initial `#line` and header include directives, and processes the root source. `process_file()` scans each line; matching quoted includes are resolved first as private, then public. Expanded private includes are written to the source stream; expanded public includes are written to the header stream. `#pragma once` is dropped.

State and persistence: global `included` and `excluded` sets control expansion across the run. Persistent artifacts are the generated source and header. The script exits immediately if an include cannot be resolved.

Dependencies and integration: it uses `argparse`, `re`, `sys`, and `os.path`. It integrates with RocksDB release/build packaging where a single-file amalgamation is useful.

Risks and test signals: the single global include set can break code that intentionally includes the same header under different preprocessor branches. Angle-bracket includes are ignored by the regex. Public/private classification depends entirely on include path ordering. Test signals include compiling the generated amalgamation, checking stable output, and exercising excluded-header behavior.
