# sources/test-tools/pynfs/nfs4.1/client41tests/environment.py

## Purpose
`client41tests/environment.py` is the shared NFSv4.1 client-test environment module. It supplies per-run configuration derived from test options, a catalog of attribute metadata, status checking helpers, invalid protocol-value generators, and convenience operations for cleanup, READDIR loops, object creation, OPEN/GETFH, and CLOSE. Test modules import this file to avoid rebuilding low-level NFSv4.1 COMPOUND sequences by hand.

## Important APIs, Types, And Functions
- `AttrInfo` records attribute name, bit number, bit mask, access string, and a sample value; its `readable`, `writable`, `mandatory`, `readonly`, and `writeonly` properties are used by attribute tests.
- `Environment(testmod.Environment)` stores `opts`, derived `root`/`home` paths, a unique timestamp, verifier state, sample file/link data, and a thread lock around verifier generation.
- `Environment.attr_info` is a source-level table of mandatory/read/write attributes and representative encoded values such as `fsid4`, `fs_locations4`, `nfsace4`, `specdata4`, `nfstime4`, and `settime4`.
- `reboot_server()`, `set_error()`, `set_error_wait_lease()`, `set_two_values()`, and `clear_two_values()` manipulate the server's exported `/config` pseudo-files to force operation errors, paired values, or reboot behavior.
- `new_verifier()` returns monotonically increasing eight-byte verifier data using wall-clock time guarded by `_lock`.
- `testname(t)` builds run-unique object names from a test code and the environment timestamp.
- `fail()`, `check()`, `checklist()`, and `checkdict()` convert protocol mismatches into `testmod.FailureException` or `WarningException`.
- `get_invalid_utf8strings()`, `get_invalid_clientid()`, `makeStaleId()`, and `makeBadID()` produce negative-test protocol values.
- `compareTimes()` compares `nfstime4` seconds/nanoseconds tuples.
- `clean_dir()`, `do_readdir()`, `use_obj()`, `create_obj()`, `create_file()`, `create_confirm()`, and `close_file()` build and execute common test compounds.

## Control Flow
The test runner constructs `Environment(opts)`, which derives a root path from `opts.path`, sets `opts.home`, and records the timestamp used for unique names and verifiers. Most lifecycle hooks (`init`, `finish`, `startUp`) are placeholders, so test-specific setup is driven by helpers called directly from client41 test modules.

Status validation flows through `check` or `checklist`: a result status is compared against one expected code or a list, the failed operation name is inferred from the last `resarray` entry when no explicit message is provided, and a test exception is raised on mismatch. Directory cleanup loops through `do_readdir`, makes each child removable by setting mode to `0o755`, tries `REMOVE`, and recursively cleans entries that return `NFS4ERR_NOTEMPTY`.

Object and file helpers compose NFSv4.1 operations using `nfs_ops.NFS4ops`. `use_obj` turns `None`, an existing filehandle, or path components into the required `PUTFH`/`PUTROOTFH`/`LOOKUP` chain. `create_file` issues `OPEN` with `OPEN4_CREATE`, adds `OPEN4_SHARE_ACCESS_WANT_NO_DELEG` unless a delegation is explicitly requested, and appends `GETFH`. `create_confirm` checks the result and returns a filehandle plus a stateid based on the `OPEN` result.

## State And Persistence Behavior
The module itself persists nothing outside process memory except when tests intentionally write server configuration pseudo-files. `Environment` stores per-run timestamp, home/root names, data samples, and verifier monotonic state. `new_verifier` is process-local and only guarantees uniqueness inside the active test process. Config writes under `/config` are interpreted by the pynfs server and can persist in that server's exported in-memory or disk-backed filesystem until reset.

## Dependencies And Integration Points
The file depends on generated NFSv4 constants and types, `nfs_ops.NFS4ops`, `nfs4client`, `nfs4lib`, `rpc.rpc`, `rpc.security.AuthSys/AuthGss`, `testmod`, and the server configuration filesystem implemented in `config.py`/`fs.py`. It integrates with `SessionRecord.compound`-style client sessions and with test modules that expect helper failures to be `testmod` exceptions.

## Risks And Edge Cases
- `check` raises a string if the caller passes a string as the expected status; that is invalid under Python 3 despite the file header claiming Python 3.2.
- `check` and `checklist` assume `nfsstat4` contains both expected and received status values.
- `do_readdir` raises `UnexpectedCompoundRes`, but this name is not imported in this file; callers may hit `NameError` if a server returns neither entries nor EOF.
- `makeStaleId` and `makeBadID` rely on CITI/Linux server-specific stateid byte layout and are deliberately marked for tests requiring those flags.
- Several default arguments are mutable dictionaries, though the functions mostly treat them as input templates.
- `set_error_wait_lease` reads a lease file and indexes `lease[1]`; malformed or short config-file content will fail before the intended wait.

## Test Signals
Strong signals are successful helper compounds, expected NFS status mismatches reported with operation names, recursive cleanup leaving empty directories, unique verifier generation, and config-driven error injection taking effect after lease waits. Negative tests should exercise invalid UTF-8 strings, stale/bad stateid helpers, wrong status paths through `check`/`checklist`, and multi-page READDIR loops.
