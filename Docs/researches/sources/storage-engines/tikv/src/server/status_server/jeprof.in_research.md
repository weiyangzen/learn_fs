# sources/storage-engines/tikv/src/server/status_server/jeprof.in

## Purpose

`jeprof.in` is a vendored Perl profiling report generator derived from gperftools `pprof` and packaged as jemalloc `jeprof`. In TiKV it is not invoked as a standalone installed binary; `profile.rs` embeds it with `include_bytes!("jeprof.in")`, writes it to a spawned `perl /dev/stdin` process, and uses it to turn a dumped heap profile plus the current TiKV executable into SVG output for `/debug/pprof/heap?jeprof=true`. The script can also operate as a full command-line profile tool for local profiles, remote pprof-compatible endpoints, raw symbolized profiles, text/callgrind/dot/svg/pdf/gif reports, listings, disassembly, collapsed stacks, and interactive exploration.

## Important APIs, Types, And Functions

- Global options and tool maps: `%obj_tool_map`, `@DOT`, `@GV`, `@EVINCE`, `@KCACHEGRIND`, `@PS2PDF`, `@URL_FETCHER`, endpoint constants for `/pprof/*`, `$address_length`, `@prefix_list`, and temporary-file globals define the script's runtime environment.
- `Init()` initializes defaults, parses CLI flags with `Getopt::Long`, validates mutually exclusive modes/granularities, determines whether the first argument is a remote profile or a symbolized profile, configures object tools, and initializes library prefix search paths.
- `Main()` is the top-level driver: fetch dynamic profiles if needed, parse one or more profile files, optionally subtract a base profile, collect symbols via local object tools or remote symbol pages, then dispatch to `FilterAndPrint()`.
- `FilterAndPrint()` performs the central analysis pipeline: total calculation, uninteresting-frame removal, focus/ignore filtering, call extraction, granularity reduction, flat/cumulative aggregation, and renderer dispatch.
- Renderers include `PrintText`, `PrintCallgrind`, `PrintDot`, `RewriteSvg`, `PrintListing`, `PrintSource`, `PrintDisassembly`, `PrintDisassembledFunction`, `PrintSymbolizedProfile`, `PrintCollapsedStacks`, and interactive wrappers in `InteractiveMode` / `InteractiveCommand`.
- Profile manipulation helpers include `FlatProfile`, `CumulativeProfile`, `RemoveUninterestingFrames`, `ReduceProfile`, `FocusProfile`, `IgnoreProfile`, `FilterFrames`, `ExtractCalls`, `AddProfile`, `SubtractProfile`, `AddEntries`, and `TotalProfile`.
- Dynamic profile support includes `ParseProfileURL`, `FetchDynamicProfile`, `FetchDynamicProfiles`, `FetchDynamicProfilesRecurse`, `TryCollectProfile`, `CheckSymbolPage`, `FetchProgramName`, and `FetchSymbols`.
- Parsing support includes the `CpuProfileStream` package for streaming binary CPU profiles, `ReadProfileHeader`, `ReadProfile`, `ReadCPUProfile`, `ReadHeapProfile`, `ReadThreadedHeapProfile`, `ReadSynchProfile`, `ReadSymbols`, and `IsSymbolizedProfileFile`.
- Symbolization and address support includes `ParseLibraries`, `FindLibrary`, `DebuggingLibrary`, `ParseTextSectionHeader*`, `ExtractSymbols`, `MapToSymbols`, `MapSymbolsWithNM`, `GetProcedureBoundaries`, `GetProcedureBoundariesViaNm`, `ShortFunctionName`, `AddressAdd`, `AddressSub`, `AddressInc`, and `HexExtend`.
- Safety/utility helpers include `ConfigureObjTools`, `ConfigureTool`, `ShellEscape`, `TempName`, `cleanup`, `sighandler`, and `error`.

## Control Flow

Startup begins in `Main()`, which calls `Init()` immediately. `Init()` creates `/tmp/jeprof$$` temporary-name roots, installs an interrupt handler, sets all `main::opt_*` flags, parses command-line options, chooses a default output mode based on whether stdout is a TTY, handles `--test`, and determines whether symbol lookup should come from local binaries, a remote `/pprof/symbol` page, or a symbolized profile file. For local binaries, it runs `ConfigureObjTools()` before any profile parsing so later symbol extraction can call `nm`, `addr2line`, `objdump`, `c++filt`, `otool`, or Windows PDB helpers.

`Main()` then calls `FetchDynamicProfiles()`. Local profile arguments are returned unchanged; remote arguments are fetched with curl into `$JEPROF_TMPDIR` or `$HOME/jeprof`. Multiple remote profiles are fetched through a fork tree. The selected profile files are parsed by `ReadProfile()`, merged with `AddProfile()` and `AddPcs()`, and optionally adjusted by `SubtractProfile()` for `--base`.

`ReadProfile()` first reads a textual or binary header. It recognizes symbolized profile sections, heap/growth profiles, threaded heap profiles, contention profiles, and binary CPU profiles. CPU profile parsing uses `CpuProfileStream` so large binary files are streamed in fixed-size windows rather than fully loaded. Heap readers parse stack entries and memory maps, adjust sampled allocations for older and v2 heap sampling algorithms, then map PCs to libraries. Contention parsing normalizes cycles to nanoseconds and handles sampling periods.

Symbol collection then branches by mode. Symbolized profiles call `FetchSymbols($pcs, $symbol_map)`. Remote profiles post PC addresses to `/pprof/symbol`. Local profiles call `ExtractSymbols()`, which maps each PC to a library range from `ParseLibraries()`, prefers debug symbol files when available, and calls `MapToSymbols()` with `addr2line`; `MapToSymbols()` falls back to `MapSymbolsWithNM()` when needed.

Finally `FilterAndPrint()` transforms and renders. It removes allocator/profiler-internal frames, applies focus and ignore regexes, reduces stack frames to the requested address/line/function/file granularity while avoiding recursion double-counting, computes flat and cumulative profiles, and dispatches to the selected renderer. Graph modes stream DOT into Graphviz or post-process generated SVG for browser pan/zoom. Interactive mode repeats a subset of those transformations per command.

## State And Persistence Behavior

The script is mostly process-local state in the `main::` namespace. Parsed options, temporary file paths, profile type, collected profile names, source-cache contents, address width, object-tool paths, and symbol disambiguation state are globals. The important persisted artifacts are:

- Temporary symbol/address files under `/tmp/jeprof$$.sym`.
- Temporary graph/listing files under `/tmp/jeprof$$.*`.
- Dynamically fetched profiles under `$JEPROF_TMPDIR` or `$HOME/jeprof`, intentionally left behind by `cleanup()` for later investigation.
- Renderer output on stdout or viewer-target temp files depending on selected mode.

`cleanup()` deletes only transient temp files and leaves fetched remote profiles. It runs on normal exit after `Main()`, on `SIGINT`, and inside `error()`. The script mutates no TiKV state directly, but when TiKV invokes it for heap SVG generation it consumes CPU, memory, temp files, the current executable, the heap profile file, and external tool processes.

## Dependencies

Runtime dependencies are Perl core modules `strict`, `warnings`, `Getopt::Long`, and `Cwd`; command-line tools include `perl`, `curl`, `nm`, `addr2line`, `objdump`, `c++filt`, optionally `dot`, `ps2pdf`, `gv`, `evince`, `kcachegrind`, `otool`, `eu-readelf`, `6nm`, and Windows PDB helpers. It assumes Unix-like process and file semantics, with limited Windows handling for `nul`, path separators, and PDB tools. For TiKV's embedded path, the critical dependencies are `perl`, object tools for the current executable, and Graphviz `dot` because `profile.rs` requests `--svg`.

## Integration Points

- `sources/storage-engines/tikv/src/server/status_server/profile.rs` uses `jeprof_heap_profile(path)` to spawn `perl`, pass this script on stdin, and run `/dev/stdin --show_bytes <current_exe> <heap_profile_path> --svg`.
- `sources/storage-engines/tikv/src/server/status_server/mod.rs` exposes heap profiling through `/debug/pprof/heap`; the query flag `jeprof=true` selects the SVG path that depends on this script.
- Remote pprof compatibility in the script expects `/pprof/profile`, `/pprof/heap`, `/pprof/symbol`, and `/pprof/cmdline`, while TiKV exposes analogous endpoints under `/debug/pprof/*`. The embedded TiKV use passes local files and does not rely on the script's remote fetch support.
- Symbolization depends on the same executable that produced the heap profile, so TiKV passes `std::env::current_exe()`.

## Risks And Edge Cases

- The embedded path blocks until the Perl process and Graphviz pipeline finish; large heap profiles or missing/slow symbol tools can make a status endpoint expensive.
- `ShellEscape()` uses a whitelist and single-quote escaping, but a few command strings are still composed manually for pipelines and redirections. Inputs are mostly local paths and tool names, but this script should not be treated as a hardened sandbox boundary.
- `jeprof_heap_profile()` unwraps when writing stdin in Rust; if the Perl child exits early, TiKV can panic in that path rather than returning a clean profiling error.
- The script relies on many external tools being available and compatible. Missing `addr2line` falls back to `nm`, but missing `dot` breaks SVG/graph output.
- Address arithmetic and parsing are hand-rolled for 32-bit and 64-bit profiles. Unit tests cover add/sub/inc, but parsing depends on profile format assumptions and Perl integer behavior.
- Dynamic remote profile fetching leaves collected profiles in `$HOME/jeprof`; this is intentional but can accumulate files outside TiKV's control if the script is used standalone.
- Heap sampling adjustment heuristics distinguish local heap-profiler output from remote heap pages; unusual profile headers can produce misleading adjusted counts.
- The script has broad legacy compatibility code. Changes that simplify one platform can silently break another profile format or output mode.

## Test Signals

- Built-in `--test` runs `RunUnitTests()`, covering `AddressAdd`, `AddressSub`, and `AddressInc` for 32-bit and 64-bit canonical hex values.
- TiKV status-server tests in adjacent Rust modules exercise `/debug/pprof/heap`, CPU pprof, and symbol endpoints; those tests are integration signals for the profile subsystem, though they may not always execute the `jeprof=true` SVG path.
- Useful manual checks are `perl jeprof.in --test`, an embedded heap SVG request with `jeprof=true`, and a failure-mode check with missing Graphviz/object tools to confirm error propagation through `profile.rs`.
