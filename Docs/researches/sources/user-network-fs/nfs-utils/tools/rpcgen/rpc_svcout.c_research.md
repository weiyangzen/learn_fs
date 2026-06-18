<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_svcout.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_svcout.c

## Purpose

`rpc_svcout.c` emits server-side RPC dispatch code, registration code, inetd/port-monitor support, timeout helpers, logging helpers, and MT-safe result cleanup scaffolding.

## Important APIs, Types, and Functions

`write_most` emits globals, auxiliaries, dispatchers, and `main` setup. `write_programs`, `write_real_program`, and `write_program` emit newstyle wrappers and per-version dispatch functions. `write_inetd_register`, `write_netid_register`, and `write_nettype_register` emit transport registration code. `write_rest` emits `svc_run`. `write_svc_aux`, `write_msg_out`, and `write_timeout_func` emit support functions. Helpers include `p_xdrfunc`, `internal_proctype`, `printerr`, `printif`, `nullproc`, `write_inetmost`, `write_pm_most`, `write_rpc_svc_fg`, and `open_log_file`.

## Control Flow

Service output parses all definitions, emits includes in `rpc_main.c`, then this file writes dispatch helpers and optionally a full `main`. Generated dispatchers switch on `rq_proc`, select argument/result XDR functions and local routines, decode args, invoke the local procedure, send replies, free args/results, and return or exit according to timer/inetd flags.

## State and Persistence Behavior

The generator writes C source to `fout` and reads global AST/options. Generated servers maintain runtime service state such as `_rpcpmstart`, `_rpcfdtype`, timeout state, and optional mutex-protected `_rpcsvcstate`; they register with portmapper/rpcb and run until `svc_run` exits or timeout logic closes them.

## Dependencies and Integration Points

It depends on ONC RPC/TIRPC server APIs, syslog, netconfig, inetd/port-monitor conventions, and shared rpcgen AST/utilities. It is coordinated by `rpc_main.c` service output and header/client emitters.

## Risks and Edge Cases

The code supports many historical modes, making option interactions high risk. Generated daemonization closes file descriptors and redirects to `/dev/console`. Timer state differs for MT and non-MT. Newstyle wrappers unpack arguments by value, so generated prototypes must match header output. Transport registration paths differ between legacy inetd and TIRPC nettype/netid modes.

## Test Signals

Generate/compile service code for legacy UDP/TCP, TIRPC netpath, explicit netid, inetd `-I`, timeout `-K`, logging `-L`, MT `-M`, newstyle `-N`, no-main `-m`, and procedures with and without explicit NULLPROC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_svcout.c -->
