# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/main.c

Main entry point and option driver for SPIN.

Key behavior:
- Parses SPIN options for verifier generation, simulation modes, LTL translation, preprocessing, trail replay, verbosity, slicing/dataflow, separate compilation, and xspin integration.
- Runs the C preprocessor into `pan.pre`, optionally creating temporary never-claim files.
- Initializes reserved symbols, parses the Promela model, parses generated LTL claims if needed, resolves loose ends, analyzes channel access, and schedules simulation or verifier generation.
- Handles LTL formulas from command-line or file and writes temporary never-claim sources.
- Provides fatal/nonfatal diagnostics, memory allocation, AST node construction, remote label/variable expressions, and token explanations.

Important details:
- Default preprocessor varies by platform, with override via `-P`.
- Cleans up generated `pan.*` files on fatal errors.
- `nn()` creates `Lextok` AST nodes and records file/line/source context.
- Tracks never-claim restrictions and warns on side effects or forbidden operations.
- `-Z` preprocess-only and `-I` inline-only exit before normal execution.

Filesystem relevance:
- Direct: creates/removes `pan.pre`, `_spin_nvr.tmp`, `*.nvr`, and generated `pan.*` files; reads model, LTL, and never-claim input files.
