<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_tblout.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_tblout.c

## Purpose

`rpc_tblout.c` emits optional `struct rpcgen_table` dispatch tables for RPC programs.

## Important APIs, Types, and Functions

`write_tables` iterates global definitions and calls `write_table` for each program. `write_table` emits one table per version, inserts a NULLPROC entry if needed, emits action pointers and argument/result XDR/size metadata, and warns when procedure numbers are out of order. `printit` formats one XDR function/size pair with tab alignment.

## Control Flow

After parsing, table output emits all program tables. For each version, expected procedure numbers start at 0 if a NULLPROC exists or 1 with an inserted null entry otherwise. Each procedure contributes a routine pointer, argument metadata, and result metadata.

## State and Persistence Behavior

The generator writes C initializer text to `fout`. It sets global `nonfatalerrors` if table order is wrong, causing rpcgen to exit nonzero while still producing output.

## Dependencies and Integration Points

It depends on `nullproc` from service output, `ptype`, `stringfix`, `locase`, AST definitions, and header support for `struct rpcgen_table` when `tblflag` is enabled.

## Risks and Edge Cases

Dispatch tables are incompatible with newstyle mode, enforced in `parseargs`. Procedure numbers are parsed with `atoi`, so symbolic procedure numbers may not sort as intended. Tab alignment assumes bounded type name lengths.

## Test Signals

Generate tables for versions with explicit and missing NULLPROC, ordered and out-of-order numeric procedures, void and non-void args/results, and verify `nonfatalerrors` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_tblout.c -->
