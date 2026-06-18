# sources/user-network-fs/samba/source3/rpc_server/mdssvc/es_parser_test.c

## Purpose
This is a standalone command-line test utility for the Spotlight-to-Elasticsearch parser. It accepts one RAW Spotlight query, loads the configured mapping JSON, prints the translated Elasticsearch query, and exits with success or failure.

## Important APIs, Types, And Functions
`main()` is the only function. It calls `lp_load_global()`, creates a talloc context, builds the default mapping path from `get_dyn_SAMBA_DATADIR()`, allows override via `elasticsearch:mappings`, loads JSON with `json_load_file()`, calls `map_spotlight_to_es_query()`, prints either the query or `*mapping failed*`, and releases Jansson/talloc resources.

## Control Flow
The program requires exactly one argument. Configuration is loaded before mapping path resolution. Any allocation, config path, JSON load, or parser failure returns exit code 1. A successful parse prints the generated query and returns 0.

## State And Persistence
The utility does not persist state. It reads Samba global configuration and a JSON mapping file, then allocates all runtime state under a process-local talloc context.

## Dependencies And Integration Points
It depends on Samba mdssvc headers, generated parser headers, mapping helpers, loadparm, dynamic path helpers, Jansson, and the same parser implementation used by the mdssvc backend. It is useful as a developer-facing test binary or manual reproducer for mapping behavior.

## Risks And Test Signals
Risks include weak diagnostics for JSON errors because it logs `strerror(errno)` rather than Jansson's detailed `json_error`, reliance on installed data paths, and no option to select alternate config except through Samba configuration. Test signals are CLI invocations for representative queries, missing/invalid mapping files, config override of mappings path, parser failure exit status, and expected stdout for known translations.
