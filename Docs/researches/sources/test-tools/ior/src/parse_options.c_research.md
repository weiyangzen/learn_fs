# sources/test-tools/ior/src/parse_options.c

Purpose: IOR-specific command-line and script parser that maps legacy IOR directives onto `IOR_param_t` plus AIORI module options.

Important APIs and functions: `ParseCommandLine()` initializes default parameters, parses CLI options, optionally reads a script, creates `IOR_test_t` nodes, allocates results, and validates run settings. `ReadConfigScript()` parses blocks between `IOR START` and `IOR STOP`, creating tests on `run` lines. `DecodeDirective()` maps one `option=value` directive to fields or backend module options. `ParseLine()` handles comma-separated directives. `createGlobalOptions()` builds the IOR global option table.

Control flow: command-line parsing starts with `init_IOR_Param_t()`, `GetPlatformName()`, global option creation, AIORI module option aggregation, `option_parse()`, and `updateParsedOptions()`. Script parsing clones previous test parameters on `run`, updates the current option table to point at the active test params, and snapshots backend options into each test. `CheckRunSettings()` defaults to write+read when no action is selected and validates dual mount constraints.

State and persistence: file-static `initialTestParams`, `parameters`, and `global_options` bridge the `-O` parser callback to current parameters. Side effects include opening `summaryFile`, truncating rank-detail CSV headers, allocating strings and option arrays, and constructing a linked list of tests.

Dependencies and integration: depends on `ior.h`, `aiori.h`, `option.c`, `utilities.c`, and IOR test construction helpers such as `CreateTest()` and `AllocResults()`. It is the main parser for the IOR benchmark rather than mdtest.

Risks: many string fields are duplicated without centralized cleanup. `ParseLine()` treats short substrings as fatal, which can reject blank comma fragments. `ReadConfigScript()` has fragile pointer use around `tail->next` when creating option tables. `DecodeDirective()` is a long manual mapping, so new `IOR_param_t` fields can be missed. Unknown directives fall back to module parsing, but error handling aborts MPI. Fixed-size buffers and `sscanf` can truncate or reject values with spaces.

Test signals: coverage should include CLI-only runs, script files with multiple `run` sections, `-O` comma directives, backend-specific options, summary formats, memory-per-node percentage parsing, dualMount validation, and unknown option failures.
