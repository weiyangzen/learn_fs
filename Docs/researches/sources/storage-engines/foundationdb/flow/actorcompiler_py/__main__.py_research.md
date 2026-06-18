## sources/storage-engines/foundationdb/flow/actorcompiler_py/__main__.py

Purpose: this Python module is the module-mode CLI for the Python port of the Flow actor compiler, allowing invocation with `python3 -m flow.actorcompiler ...`.

Important APIs: `parse_arguments()` implements the same user-facing shape as the C# tool: required input/output plus `--disable-diagnostics` and `--generate-probes`; missing operands print usage and exit `100`. `overwrite_by_move()` makes an existing target writable, unlinks it, atomically replaces via `os.replace`, and marks the final file read-only. `main()` reads input, constructs `ActorParser`, writes generated output and `.uid`, and maps `ActorCompilerError` to FAC1000/exit `1` and unexpected exceptions to traceback plus FAC2000/exit `3`.

Control flow: parse args, announce command, compile to output temp, replace generated output, compile UID sidecar to the same temp path, replace UID, return success. Error paths remove temp and generated output if present.

State and persistence behavior: output files are rewritten from temporary files and then chmodded read-only for parity with the C# compiler. UID records are persisted as `hi|lo|source-key`. No persistent state exists beyond these files.

Dependencies and integration points: imports `ActorParser`, `ErrorMessagePolicy`, and `ActorCompilerError` from the Python actorcompiler package. Intended for build systems or comparison harnesses during migration from the C# compiler.

Risks: the code uses `Path.with_suffix(output_path.suffix + ".tmp")` and `.uid`, which gives paths like `file.g.cpp.tmp` and `file.g.cpp.uid`; this matches intent but differs from simple string append only for suffix-less paths. Broad exception handling prints a traceback, which is useful for migration but noisier than the C# FAC2000 path.

Test signals: CLI parity tests with the C# compiler, exit-code tests, FAC1000/FAC2000 diagnostics, chmod/read-only checks, and output/UID comparison are the primary validation.
