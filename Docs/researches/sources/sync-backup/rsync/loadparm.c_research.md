# sources/sync-backup/rsync/loadparm.c

## Purpose
`loadparm.c` parses rsync daemon configuration parameters and exposes generated `lp_*()` accessors for global and per-module settings. It is based on Samba's loadparm model, trimmed for rsync daemon modules.

## Important APIs, Types, and Functions
Key public functions are `reset_daemon_vars()`, `lp_load()`, `set_dparams()`, `lp_num_modules()`, and `lp_number()`. Important internal helpers include `expand_vars()`, `string_set()`, `copy_section()`, `init_section()`, `strwiEQ()`, `getsectionbyname()`, `add_a_section()`, `map_parameter()`, `set_boolean()`, `do_parameter()`, and `do_section()`. Accessors are generated via `FN_GLOBAL_*` and `FN_LOCAL_*` macros from `daemon-parm.h`.

## Control Flow
`lp_load()` resets `Vars`, starts in the global section, and delegates parsing to `pm_process()` with callbacks. `do_section()` handles real module sections plus special push/pop/reset directives used by include processing. At the first transition out of global scope, it applies command-line daemon parameters from `--dparam`. `do_parameter()` maps a label to `parm_table`, rejects global-only parameters in module sections, expands `%ENV%` references immediately for non-string types, parses the typed value, and stores it in either `Vars.g`, `Vars.l`, or the current module section. `lp_number()` resolves a loaded module by name after parsing.

## State and Persistence
State is process-local: `Vars`, `Defaults`, `Vars_stack`, `section_list`, `iSectionIndex`, and `bInGlobalSection`. String settings are duplicated but intentionally not freed because daemon config is loaded once per long-lived listener or once per forked job. Environment expansion may allocate a replacement string lazily the first time an accessor is called.

## Dependencies and Integration Points
The file depends on `rsync.h`, `itypes.h`, `ifuncs.h`, `default-dont-compress.h`, generated `daemon-parm.h`, `dparam_list`, `pm_process()`, and logging via `rprintf()`. Daemon startup, authentication, logging, module selection, and transfer policy use the generated `lp_*()` accessors.

## Risks
Parsing is sequence-dependent, especially around global-to-module boundaries and include stack restoration. Unknown parameters are logged but ignored during normal load, while syntax-check mode rejects them. Environment expansion has a fixed extra buffer allowance and exits on overflow. The intentional memory leaks are acceptable for current daemon lifecycle assumptions but would matter if configs were reloaded repeatedly in one process.

## Test Signals
Tests should parse configs with global and module sections, duplicate modules, whitespace-insensitive names, invalid section names containing `/`, `--dparam` overrides, boolean reverse and tri-state values, enum values, path slash trimming, `%ENV%` expansion, include push/pop/reset behavior, and syntax-check rejection of unknown parameters.
