## sources/storage-engines/foundationdb/flow/actorcompiler/Program.cs

Purpose: this C# file is the command-line entry point for the original actor compiler executable. It reads an input `.actor.cpp`, runs `ActorParser`, writes generated C++ to the requested output file, and writes a UID sidecar file.

Important APIs: `Main(string[] args)` parses `<input> <output> [--disable-diagnostics] [--generate-probes]`, configures `ErrorMessagePolicy`, constructs `ActorParser`, calls `parser.Write`, and serializes `parser.uidObjects` as `hi|lo|source-key` lines. `OverwriteByMove` replaces an output through a temporary file, normalizes the old target to writable before deletion, moves the temp file into place, then marks the result read-only.

Control flow: invalid arity prints usage and returns `100`. Actor-language errors return `1` with FAC1000 diagnostics and output cleanup. Unexpected exceptions return `3` with FAC2000 diagnostics and output cleanup. Success returns `0` after writing both generated output and `.uid`.

State and persistence behavior: file persistence is explicit and atomic-ish by temp-write plus move. Outputs are made read-only. On failures, the temporary and generated output are deleted; the code does not explicitly delete an already-written UID sidecar if the second phase fails after output replacement.

Dependencies and integration points: depends on the C# parser/compiler and `System.IO`. Build systems invoke this executable as a preprocessing step before compiling generated C++.

Risks: command-line parsing silently ignores unknown `--` options. `OverwriteByMove` deletes and moves instead of an atomic replace operation on all platforms, so interruption can leave no target file. The UID sidecar path is simply `<output>.uid`.

Test signals: CLI tests should verify exit codes, usage behavior, read-only output attributes, diagnostic toggles, probe generation flag forwarding, UID sidecar creation, and cleanup behavior after parser/compiler errors.
