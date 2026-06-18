# sources/test-tools/pynfs/nfs4.1/nfs_ops.py

## Purpose
`nfs_ops.py` provides dynamic builders for NFSv4 operations, NFSv4 callback operations, and NFSv3 procedure argument objects. It hides generated XDR constructor names behind concise methods such as `op.putfh(...)`, `op.open(...)`, or `op.cb_recall(...)`.

## Important APIs, Types, and Functions
- `nfs4_op_names()` derives lower-case operation names from `nfs4_const.nfs_opnum4` and callback names from `nfs_cb_opnum4`.
- `nfs3_proc_names()` derives lower-case NFSv3 procedure names from constants beginning with `NFSPROC3_`.
- `NFSops.__getattr__` returns a lambda for recognized operation names.
- `NFSops._handle_op()` creates the matching generated `*_args` class and wraps NFSv4 args in `nfs_argop4` or `nfs_cb_argop4`.
- `NFS3ops` and `NFS4ops` specialize the base class for protocol version.

## Control Flow
When a caller accesses `op.lookup`, `__getattr__` checks the derived operation list and returns a function that forwards to `_handle_op`. For NFSv4, `_handle_op` looks up the operation number constant, instantiates an args class if present, places it into the correct union keyword, and returns the generated argop object. For NFSv3 it returns the generated args instance directly.

## State and Persistence Behavior
The object holds immutable protocol metadata after construction: selected type module, constant module, suffix, and op prefix. It has no persistent external state.

## Dependencies and Integration Points
The module depends on generated `xdrdef.nfs4_type`, `nfs4_const`, `nfs3_type`, and `nfs3_const`. It is used throughout server tests, callback code, client helpers, and server implementation to build COMPOUND operation arrays.

## Risks and Edge Cases
Unknown attributes return `None` implicitly instead of raising `AttributeError`, which can make mistakes fail later. Dictionary-typed generated classes get special handling that assumes exactly one argument. The dynamic naming contract depends tightly on generated XDR class names and constants.

## Test Signals
Almost every test file in this group imports `NFS4ops()` and would fail quickly if operation packing broke. Specific signals include successful COMPOUND construction, callback argop construction, and correct behavior for illegal or undefined opcodes in `st_compound.py`.
