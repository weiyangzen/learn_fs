# sources/test-tools/syzkaller/pkg/clangtool/clangtool.go

Purpose: Go-side runner for compiled-in clang tools. It loads a kernel `compile_commands.json`, invokes the current test/tool binary in a special environment for each source file, merges JSON output, verifies source locations, and caches final output.

Important APIs/types/functions: `Config`, generic `OutputDataPtr[T]`, `Run`, `Verifier`, `NewVerifier`, `Verifier.Error`, `Verifier.Filename`, `Verifier.LineRange`, `runTool`, `loadCompileCommands`, and `SortAndDedupSlice`.

Control flow: `Run` first attempts to read `CacheFile`. On cache miss it loads compile commands, starts `runtime.NumCPU()` workers, calls `runTool` for each file, merges each output via `OutputPtr.Merge`, finalizes, verifies all recorded files/ranges, and writes the cache. `runTool` executes `os.Args[0]` with clang-tool flags and `SYZ_RUN_CLANGTOOL=<tool>`, parses JSON, and normalizes emitted paths relative to the kernel source tree.

State and persistence behavior: Persistent state is the optional JSON cache file. `Verifier` caches file line counts in memory, using `-1` for missing files. `loadCompileCommands` shuffles command order intentionally to catch nondeterministic merge behavior.

Dependencies/integration points: Uses `pkg/osutil` for JSON/file helpers. Output types must implement merge/source/finalize hooks, which `codesearch.Database` does. The C++ clang tool is expected to intercept execution when `SYZ_RUN_CLANGTOOL` is set; otherwise `init` panics to signal missing compiled-in tool support.

Risks: Cache reads bypass verification of freshness or tool/schema version unless the caller encodes it in `CacheFile`. `SortAndDedupSlice` deduplicates by marshaled JSON SHA-256, so equality depends on stable JSON representation. Running one process per compile command can be expensive on huge databases, though workers bound concurrency to CPU count.

Test signals: Used by `clangtool/tooltest` and `codesearch` tests. Error wrapping includes stderr for failed tool invocations, and verifier failures detect stale or bogus locations before downstream consumers use them.
