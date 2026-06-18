# File Research: sources/os/plan9/9front/sys/src/cmd/spin/main.c

`main.c` is Spin’s command-line front end and lifecycle coordinator. It parses options, invokes the C preprocessor, parses Promela, handles LTL/never-claim injection, chooses simulation vs verifier-generation modes, optionally compiles/runs `pan`, and cleans up temporary/generated files.

Major paths include plain parsing/simulation, `-a` verifier generation, `-run`/`-search` generate-compile-run flow, `-replay` trail replay, `-t` guided trail interpretation, `-f`/`-F` LTL translation, `-N` external never claim inclusion, `-pp` pretty-printing, `-M` MSC/Tcl output, and xspin/internal modes. `preprocess()` builds the preprocessor command from `PreProc` and accumulated `-D`/`-U`/`-E` arguments and writes `pan.pre`.

`alldone()` owns cleanup and the post-parse automation path. In buzzed verifier modes it may replay with Spin itself, reuse or compile `pan.c`, add compile-time macros and runtime flags, run swarm/biterate iterative searches, randomize hash/search parameters, and remove generated `pan.*` files afterward. `final_fiddle()`, `add_runtime()`, and `add_comptime()` translate high-level search options into `pan` compile/runtime options.

`main()` also initializes predefined symbols, seeds Spin’s RNG, parses the model with `yyparse()`, optionally parses generated LTL claims, fixes loose graph ends, performs channel access analysis, disables incompatible statement merging when needed, runs source analysis optimizations, schedules/interprets the model, and exits through `alldone()`.

Supporting functions include `non_fatal()`/`fatal()` diagnostics, zeroing allocator `emalloc()`, access tracking through `setaccess()` and `trapwonly()`, AST node construction in `nn()`, remote label/variable expression builders `rem_lab()`/`rem_var()`, and `explain()` for token names used in diagnostics.

Important risks: command strings are assembled into fixed buffers and executed through `system()`; option parsing mutates global mode flags with broad downstream effects; temporary files have fixed names such as `pan.pre` and `_spin_nvr.tmp`; and many syntax checks depend on global parser state (`context`, `claimproc`, `lineno`, `Fname`).
