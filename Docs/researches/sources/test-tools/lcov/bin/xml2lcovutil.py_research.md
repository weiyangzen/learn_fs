# sources/test-tools/lcov/bin/xml2lcovutil.py Research

Purpose: `xml2lcovutil.py` is the shared Cobertura XML to LCOV implementation used by both `xml2lcov` and `py2lcov`. It writes LCOV records for files, functions, branches, lines, totals, optional checksums, and optional source versions.

Important APIs and types: `line_hash(line)` computes LCOV-compatible base64 MD5 line checksums. `ProcessFile` is the main class. Its constructor parses exclude patterns/version-script settings, opens output, records Python mode, and writes `TN`. `process_xml_file()` parses Cobertura structure and resolves filenames through XML `<sources>`. `process_file()` emits per-file LCOV records and derives functions/branches/line records. `close()` closes the output and may invoke `lcov` to append versions when the configured version script is a Perl module.

Control flow: XML processing requires top-level `sources` and `packages`. Each package marks external dotted package names specially; non-external filenames are searched under each source path. Matching files are written as `SF`, optional `VER`, processed, and closed by `end_of_record`. File processing optionally reads source code for checksums or Python function derivation, parses XML `methods` blocks into function metadata, then parses `lines`, totals hits, derives Python function scopes from indentation and `def`/`class`, lowers Python declaration-line hits when function bodies are unexecuted, emits branch `BRDA` records from condition coverage, then emits `FNL`/`FNA`, `DA`, `LF`/`LH`, `BRF`/`BRH`, and `FNF`/`FNH`.

State and persistence: object state includes parsed args, output handle, exclude/version settings, and Python mode. It persists only the output info file; source path use counters are local diagnostics.

Dependencies and integration: integrates Cobertura/Coverage.py XML with LCOV. Optional post-processing shells out to sibling `lcov` for Perl version scripts, checksum, branch coverage, and function coverage flags.

Risks: branch identity is a lower-bound approximation because XML gives only hit/total counts. The source resolver prints an undefined last `path` when no sources exist. XML parsing uses asserts for condition fields, which can abort. Function derivation is indentation based and can miss decorators, multiline definitions, async defs, or nonstandard formatting. `close()` references `deriveFunctions` even for callers that may not define it.

Test signals: exercise source path resolution, unused-source warnings, external package filenames, method-derived functions, Python indentation-derived functions/classes/nesting, branch condition coverage, checksum generation, missing source files with `--keep-going`, Perl-module version scripts, and malformed XML structures.
