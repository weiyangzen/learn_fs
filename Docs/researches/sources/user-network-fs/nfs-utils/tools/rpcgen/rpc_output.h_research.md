<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_output.h -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_output.h

## Purpose

`rpc_output.h` is a small declaration header for selected rpcgen output helper functions.

## Important APIs, Types, and Functions

It declares `write_msg_out`, `nullproc`, `printarglist`, and `pdeclaration` behind include guard `RPCGEN_NEW_OUTPUT_H`.

## Control Flow

There is no runtime flow. Translation units can include it to call output helpers shared between client, server, header, and service generation.

## State and Persistence Behavior

No state is declared here. The functions operate on global output/parser state defined elsewhere.

## Dependencies and Integration Points

It depends on `proc_list` and `declaration` types being visible before inclusion. In this source tree, `proto.h` provides a broader and more actively used internal prototype set.

## Risks and Edge Cases

The signatures here are less const-correct/differently typed than the prototypes in `proto.h`, so including both under strict C modes could expose conflicts. Its limited use suggests it may be legacy residue.

## Test Signals

Compile all rpcgen translation units with warnings enabled and check for prototype conflicts or unused-header drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_output.h -->
