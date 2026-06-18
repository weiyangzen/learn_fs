# sources/test-tools/pynfs/nfs4.0/nfs_ops.py

## Purpose
`nfs_ops.py` is a convenience factory for building NFSv3 procedure argument instances and NFSv4 operation wrapper structures from generated XDR type modules. It lets tests call `op.lookup(name)` or `op.getattr(mask)` instead of manually constructing `LOOKUP4args`, `nfs_argop4(OP_LOOKUP, oplookup=...)`, and equivalent callback wrappers.

## Important APIs, Types, And Functions
- `nfs4_op_names()` derives lowercase operation names from `nfs4_const.nfs_opnum4` and callback operation names from `nfs_cb_opnum4`.
- `nfs3_proc_names()` derives lowercase NFSv3 procedure names from constants named `NFSPROC3_*`.
- `NFSops.__init__(is_v4)` selects type/constant modules, operation names, argument suffixes, and opcode prefixes for v3 or v4.
- `NFSops.__getattr__(attrname)` dynamically returns a lambda builder when `attrname` is a known operation/procedure name.
- `NFSops._handle_op(opname, args)` constructs the matching generated argument class and wraps it in `nfs_argop4`/`nfs_cb_argop4` for v4, or returns the generated procedure args for v3.
- `NFS3ops` and `NFS4ops` are thin typed constructors.

## Control Flow
Callers instantiate `NFS4ops()` or `NFS3ops()`. Accessing a valid operation name triggers `__getattr__`, returning a function that captures the operation name and forwards positional arguments to `_handle_op`. `_handle_op` uppercases the operation, finds the generated `*4args` or `*3args` class, constructs it when needed, looks up the opcode constant, then returns a generated wrapper. For NFSv4 callback operation names beginning with `CB_`, it uses `nfs_cb_argop4` and the `opcb...` keyword; otherwise it uses `nfs_argop4` and `op...`.

## State And Persistence Behavior
Instances store only immutable factory configuration: whether they are v4, selected module references, operation names, suffixes, and prefixes. There is no persistence, caching of generated operations, or external state mutation.

## Dependencies And Integration Points
The module depends on `xdrdef.nfs4_type`, `xdrdef.nfs4_const`, `xdrdef.nfs3_type`, and `xdrdef.nfs3_const`. It is used broadly in the `servertests` package and in delegation callback helpers to build compounds. Its output structures are consumed by `NFS4Client.compound`, server dispatch, packers, and callback servers.

## Risks And Edge Cases
- Unknown attributes return `None` from `__getattr__` rather than raising `AttributeError`, which can mask typos until call time.
- The special `if type(klass) is dict` branch suggests generated type metadata can be a dict; callers must pass exactly one prebuilt argument for that path.
- Operation names are derived from constant dictionaries at import/runtime, so generated XDR naming changes directly alter the dynamic API surface.
- There is no keyword-argument support; all operation argument constructors must be satisfied positionally.

## Test Signals
All server tests in this group use `op = nfs_ops.NFS4ops()` for raw operation construction. Failures in this factory surface as malformed compounds, packer errors, or wrong `resop`/argument union fields in ACCESS, COMPOUND, CREATE, LINK, LOCK, DELEGRETURN, and GSS scenarios.
