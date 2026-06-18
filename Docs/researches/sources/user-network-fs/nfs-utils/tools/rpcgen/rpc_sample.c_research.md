<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_sample.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_sample.c

## Purpose

`rpc_sample.c` emits optional sample client and server implementation templates for parsed RPC programs.

## Important APIs, Types, and Functions

`write_sample_svc` emits server templates for `DEF_PROGRAM` definitions. `write_sample_clnt` emits sample client functions per version and returns a count. `write_sample_client` declares arguments/results, creates a client handle, calls generated stubs, and reports failures. `write_sample_server` emits placeholder service routines and MT free-result helpers. `add_sample_msg` prints the sample-code banner. `write_sample_clnt_main` emits a simple `main` that calls all generated sample clients. `return_type` wraps shared `ptype`.

## Control Flow

Sample output modes parse definitions, then for each program version emit either client demo functions or server skeleton functions. Client sample generation also emits a main function when at least one program exists.

## State and Persistence Behavior

The generator writes template C source to `fout` and reads global AST/options. Generated sample programs contain placeholder local variables and user-fill sections; they do not persist runtime state by themselves.

## Dependencies and Integration Points

It depends on `printarglist`, `pvname`, `pvname_svc`, `ptype`, and flags such as `Cflag`, `newstyle`, `mtflag`, and `tirpcflag`. It is invoked by `rpc_main.c` for `-Sc`, `-Ss`, and `-a`.

## Risks and Edge Cases

Generated samples are scaffolding, not complete applications. Some declarations are uninitialized by design. Transport choice differs for TIRPC (`netpath`) versus legacy (`udp`). The string comparison `strcmp(l->decl.type, "string") == 1` looks suspicious and likely intended nonzero comparison, though output impact is limited formatting.

## Test Signals

Generate sample clients/servers for void, string, multi-argument, MT-safe, and multiple-version programs; compile the templates enough to catch syntax errors; inspect placeholder result and free-result code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_sample.c -->
