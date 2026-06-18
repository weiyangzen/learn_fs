<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.c

## Purpose

`rpc_util.c` provides shared global state and utility functions for rpcgen parsing, type handling, output formatting, diagnostics, cleanup, and basic type metadata.

## Important APIs, Types, and Functions

It defines scanner globals (`curline`, `where`, `linenum`, `infilename`), IO globals (`fin`, `fout`), output tracking (`outfiles`, `nfiles`), and the global AST list `defined`. `reinitialize`, `findval`, and `storeval` manage parser state. `fixtype`, `stringfix`, `ptype`, and `isvectordef` guide C type output. `locase`, `pvname`, and `pvname_svc` form generated symbol names. `error`, `crash`, `expected1/2/3`, `printwhere`, and `record_open` handle diagnostics and cleanup. `make_argname`, `add_type`, and `find_type` support newstyle args and inline XDR generation.

## Control Flow

Parser and generator modules call these helpers throughout generation. Fatal errors print source context and invoke `crash`, which unlinks recorded output files and exits. Default generation calls `reinitialize` between passes to reset scanner and AST state.

## State and Persistence Behavior

Most rpcgen shared state lives here for the lifetime of the process. Persistent effects are cleanup-related: generated output paths recorded by `record_open` may be unlinked on fatal errors.

## Dependencies and Integration Points

It depends on token and AST headers, POSIX `unlink`, and all generator modules. `rpc_main.c` initializes basic types and uses output tracking, while parser/scanner use diagnostics and globals.

## Risks and Edge Cases

Memory ownership is intentionally process-lifetime and not freed between passes beyond resetting pointers, so long-running embedding would leak. `locase` uses a static 100-byte buffer. `record_open` tracks only seven files. `streq` assumes non-NULL inputs. Fatal cleanup can unlink outputs from current generation if paths were recorded.

## Test Signals

Tests should cover fatal cleanup, source-position diagnostics, typedef chain fixing, vector typedef detection, basic type lookup, output file tracking limits, generated symbol casing, and reinitialization between multi-output generation passes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.c -->
