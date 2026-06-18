# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/summarize.py

Purpose: converts FoundationDB trace files and test process metadata into compact Joshua-compatible XML/JSON summaries, including errors, warnings, coverage, timeout, Valgrind, stderr, and determinism signals.

Important APIs/types: `SummaryTree`, `ParseHandler`, `Parser`, `XmlParser`, `JsonParser`, `Coverage`, `TraceFiles`, and `Summary`. `Summary.register_handlers()` installs event callbacks for ProgramStart, Simulation, ElapsedTime, warnings/errors, CodeCoverage, test counts, severity remaps, buggify/fault injection, stderr severity, and random reseeds.

Control flow: `Summary.summarize()` groups trace files by timestamp, parses the newest run, writes FDB coverage when configured, and calls `done()`. `done()` finalizes pass/fail state, adds warning/error limits, timeout, peak memory, Valgrind parse results, missing TestEnd, stderr truncation, and final `Ok`/`Runtime` attributes.

State and persistence: in-memory summary tree and coverage map; optional FDB coverage writes; reads trace files from run dirs.

Dependencies and integration: config, XML/JSON parsers, Valgrind parser, FDB persistence, and `run.py`.

Risks and test signals: XML parser ignores fatal errors; `negative_test_success` iterates attrs incorrectly; trace filename timestamp parsing assumes fixed dot layout; stderr defaults to severity 40. Tests should cover JSON/XML traces, no traces, missing elapsed time, valgrind leaks ignored, severity remap, negative tests, and output format serialization.
