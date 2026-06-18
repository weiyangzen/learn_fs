# sources/test-tools/lcov/bin/xml2lcov Research

Purpose: `xml2lcov` is a small executable Python front end for translating Cobertura-style XML coverage reports to LCOV tracefiles using `xml2lcovutil.ProcessFile`.

Important APIs and functions: `main()` defines the CLI and delegates all XML semantics. Supported options are `--output`, `--test-name`/`--testname`, `--exclude`, `--verbose`, `--version-script`, `--checksum`, and `--keep-going`; positional inputs are XML files.

Control flow: the script builds help text from `ProcessFile.usageNote`, parses arguments, fails immediately if no inputs are present, constructs one `ProcessFile(args)` so all input XML files are appended to the same output stream, calls `process_xml_file()` for each input in order, and closes the processor.

State and persistence: the only file it writes directly is the LCOV output configured on `args.output`; all parsing state and optional version-script post-processing live in `ProcessFile`.

Dependencies and integration: it imports standard Python XML, path, pattern, subprocess, hashing modules plus the local `xml2lcovutil.py`. It is a simple LCOV-suite adapter for Cobertura XML producers and is intended to feed generated info back into `lcov` for richer filtering/substitution support.

Risks: there is no top-level exception handling around malformed XML unless `ProcessFile` catches it internally. The help text says input files are "python coverage data" although this tool expects XML. Feature parity is intentionally limited compared with Perl LCOV tools.

Test signals: test missing input rejection, multiple XML files in one output, excluded filename patterns, checksum behavior with present and missing source files, version-script errors under `--keep-going`, malformed source/package XML structure, and branch totals from condition-coverage fields.
