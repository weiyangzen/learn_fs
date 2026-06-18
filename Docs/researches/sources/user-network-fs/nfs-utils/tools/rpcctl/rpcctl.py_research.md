<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcctl/rpcctl.py -->
# sources/user-network-fs/nfs-utils/tools/rpcctl/rpcctl.py

## Purpose

`rpcctl.py` is a sysfs inspection/control utility for Linux SunRPC clients, xprt switches, and individual transports. It shows connection state and can alter transport state, destination addresses, add transports, or remove non-main transports.

## Important APIs, Types, and Functions

Top-level initialization locates the sysfs mount from `/proc/mounts` and verifies `kernel/sunrpc`. Helpers `read_sysfs_file`, `write_sysfs_file`, and `read_info_file` handle sysfs data. `Xprt` models one transport and supports display, `set_dstaddr`, `set_state`, `remove`, lookup, and argparse command registration. `XprtSwitch` models an xprt switch, supports display, `add_xprt`, and dstaddr changes across contained xprts. `RpcClient` models an RPC client and links to its switch. `show_small_help` handles no-command invocation.

## Control Flow

Import-time code fails early if sysfs or sunrpc sysfs is unavailable. The parser adds `client`, `switch`, and `xprt` command families. Lookups traverse `sunrpc/rpc-clients` and `sunrpc/xprt-switches`. Mutating commands write sysfs control files and then refresh or print affected objects.

## State and Persistence Behavior

The script persists no files. Mutations write kernel sysfs attributes such as `xprt_state`, `dstaddr`, and `add_xprt`, changing live RPC transport state. Object instances cache some info from construction and refresh state selectively.

## Dependencies and Integration Points

It depends on Python 3, pathlib, argparse, DNS resolution via `socket.gethostbyname`, `/proc/mounts`, and the kernel SunRPC sysfs ABI. It is tightly integrated with RPC client transport management and NFS multipath/session diagnostics.

## Risks and Edge Cases

Import-time sysfs validation makes unit testing harder unless `/proc/mounts` is mocked. Path parsing assumes xprt directory names contain the transport type at `split("-")[2]`. Some lookup paths construct objects without explicit existence checks and can fail later. Mutating main xprts is blocked in code, but races with kernel removal are only partly handled by `__str__`. `except Exception` at top-level prints only the message.

## Test Signals

Tests should build fake sysfs trees for clients, switches, and xprts; cover missing sysfs/sunrpc; verify show output, missing files as `(enoent)`/custom labels, main-xprt mutation rejection, xprt removal sequence, dstaddr resolution, add-xprt writes, and kernel removal races.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcctl/rpcctl.py -->
