# sources/storage-engines/foundationdb/contrib/serialize-check/script/renormalize.py

## Purpose
`renormalize.py` orchestrates FoundationDB serialization inventory generation. It reads a compilation database, selects relevant C++ source files, runs the `source_scanner` LibTooling executable over those files in parallel, deduplicates discovered serializable classes, and writes a Markdown report of member variables and raw serialize bodies.

## Important APIs, Types, And Functions
- `_setup_args()` defines CLI options: `--source-scanner`, `--extra-arg`, `--compilation-database`, and `--num-workers`.
- `CompilationDatabase` loads `compile_commands.json`, computes a common source base directory from all `file` entries, stores source-relative compile flags, and exposes `iterate_files()`.
- `CompilationDatabase._get_options(command)` strips the compiler executable from a command string using `split(" ", 1)[1]`.
- `CompilationDatabase.iterate_files()` yields only `.cpp` files whose relative path includes one of `flow/`, `fdbcli/`, `fdbserver/`, `fdbclient/`, or `fdbrpc/`.
- `SerializableObjectLibrary` stores scan results in a nested `defaultdict(dict)` keyed by path and class name. `accept` deduplicates a class for a path, and `generate_report` writes sorted Markdown sections.
- `SourceScanner` wraps subprocess invocation of `source_scanner`. `scan(source_path)` runs `[source_scanner_path, source_path, "-p", compilation_database_path]`, optionally appending `--extra-arg`, logs stderr, decodes JSON lines from stdout, normalizes `sourceFilePath` relative to the project base directory, and returns parsed items.
- `_main()` wires arguments, logging, defaults, `CompilationDatabase`, `SerializableObjectLibrary`, `SourceScanner`, multiprocessing, and output file generation.

## Control Flow
At startup `_main` picks defaults of `./source_scanner` and `./build/compile_commands.json` relative to the current working directory unless CLI options override them. It loads the compilation database, asserts a base directory, creates a scanner, and obtains a generator of selected paths. A `multiprocessing.Pool(args.num_workers)` maps `SourceScanner.scan` over those paths. For each returned JSON item, `_main` records `sourceFilePath`, `className`, `variables`, and raw serialize code in the library. Finally it writes `SerialzedObjects.md` in the current working directory and returns 0.

The intended workflow from the README is to generate a FoundationDB compilation database with `OPEN_FOR_IDE=ON`, then run this script from the FDB root with the scanner binary available. The generated Markdown is intended for comparison between versions.

## State And Persistence Behavior
The script reads persistent build metadata from `compile_commands.json` and writes one persistent artifact, `SerialzedObjects.md` (note the misspelling in the filename). All intermediate scan results are kept in memory until report generation. Logging goes to stderr via `logging.basicConfig(level=logging.DEBUG)`. It does not update the compilation database or source files.

## Dependencies And Integration Points
Runtime dependencies are Python standard library modules (`argparse`, `collections`, `io`, `logging`, `json`, `multiprocessing`, `os`, `pathlib`, `subprocess`, `sys`) and an external `source_scanner` executable. It depends on compile database records containing `file` and `command` fields. It integrates with `SourceScanner.cpp` through line-delimited JSON fields `sourceFilePath`, `className`, `variables`, and `raw`.

## Risks And Edge Cases
- `_get_options` naively splits the compile command string on the first space. It does not support `compile_commands.json` entries that use `arguments` instead of `command`, quoted compiler paths with spaces, or malformed command strings.
- `_base_directory` is the common path of every file in the database, not necessarily the repository root. If the database includes generated or external files, relative paths and filtering may be surprising.
- `iterate_files` uses substring checks such as `"flow/" in key`; this can match nested paths unexpectedly and excludes headers or non-`.cpp` files that might contain serializable classes.
- `SourceScanner.scan` does not pass `check=True` and does not fail on nonzero return codes. It logs stderr but then attempts to parse stdout, so partial failures can silently produce incomplete reports.
- JSON parse errors from scanner output are not caught.
- Multiprocessing requires `SourceScanner` and its contained paths to be pickleable; that is true for current fields but can be fragile if scanner state gains unpickleable members.
- `SerializableObjectLibrary.accept` silently keeps the first class found for a path/class pair. If multiple definitions or template specializations differ, later results are dropped without diagnostics.
- The output filename differs from the README's later text (`SerialzedObjects.md` in code versus README prose also mentioning `SerializedObjects.md`), which can confuse consumers.
- The report emits Markdown code blocks containing raw C++ without escaping triple backticks inside raw text, though serialize bodies are unlikely to contain them.

## Test Signals
Focused tests can feed a small synthetic compilation database into `CompilationDatabase` and assert base directory, relative path filtering, and command option extraction. `SourceScanner.scan` should be tested with a fake executable that emits line-delimited JSON and stderr. End-to-end smoke coverage should run with a tiny C++ project and confirm `SerialzedObjects.md` contains sorted paths/classes, member variable numbering, and raw serialize code. Failure tests should cover missing scanner, nonzero scanner exit, malformed JSON, `arguments`-only compilation databases, and scanner stderr.
