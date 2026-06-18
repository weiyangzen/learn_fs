<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_main.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_main.c

## Purpose

`rpc_main.c` is the top-level driver for the bundled `rpcgen` compiler. It parses command-line options, runs the C preprocessor, coordinates parsing, selects output modes, opens/closes generated files, and manages cleanup on fatal errors.

## Important APIs, Types, and Functions

`struct commandline` records selected output mode and paths. `main` dispatches to `c_output`, `h_output`, `l_output`, `s_output`, `t_output`, `svc_output`, `clnt_output`, or `mkfile_output`. `open_input` forks/execs `cpp` with `-C` and mode defines; `close_input` checks preprocessor status. `open_output`, `close_output`, `record_open`, and `checkfiles` protect output files. `parseargs` owns option validation and global flags. `do_registers` emits service registrations. `generate_guard`, `extendfile`, `mkfile_output`, and `c_initialize` provide support.

## Control Flow

The driver parses options, checks input/output conflicts, and either generates one requested artifact or the default set of XDR, header, client, server, optional table, sample, and Makefile outputs. Between default outputs it calls `reinitialize` because preprocessing/parsing is repeated per artifact. Each output mode opens preprocessed input, emits a warning banner and includes, parses definitions into global `defined`, calls the relevant emitter, and closes input/output.

## State and Persistence Behavior

Global option flags (`inetdflag`, `pmflag`, `newstyle`, `tirpcflag`, `mtflag`, etc.), output tracking arrays, preprocessor process id, and parser globals are process state. Persistent effects are generated output files; `crash` unlinks files recorded by `record_open` on fatal errors.

## Dependencies and Integration Points

It depends on POSIX process/file APIs, a C preprocessor at `/lib/cpp` or `cpp`, gettext/nls, parser/scanner modules, and all output modules. Generated code targets ONC RPC/TIRPC APIs depending on options.

## Risks and Edge Cases

`checkfiles` refuses existing output files, including sample and Makefile outputs, with an overwrite warning then crash. Argument parsing uses a fixed `arglist` length for cpp defines. Default TIRPC/inetd interactions are subtle: `pmflag` is derived from `tirpcflag` and `inetdflag`. Some output modes may unlink generated files when no applicable definitions are found. `parseargs` restricts `-s` to `udp`/`tcp` early even though later TIRPC valid nettypes are broader for other paths.

## Test Signals

Run smoke tests for every generation flag, default generation, `-a`, `-N`, `-M`, `-T`, `-I`, `-K`, `-5`, `-b`, `-Y`, `-D`, stdin/stdout modes, existing-output failures, missing cpp, cpp failures, and cleanup of partial outputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_main.c -->
