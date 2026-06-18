# sources/test-tools/pynfs/nfs4.1/config.py

## Purpose
`config.py` defines the server configuration model exposed by the NFSv4.1 test server, especially values surfaced through the pseudo-filesystem under `/config`. It provides typed `ConfigLine` entries, metaclass-generated config properties, server-wide values, per-client limits, per-operation error injection state, and action triggers such as reboot.

## Important APIs, Types, And Functions
- `ConfigAction` is raised by verifier functions when a config write should trigger behavior rather than simply store a value.
- `_action`, `_int`, `_bool`, `_statcode`, and `_opline` verify and coerce text written through config files.
- `_opline(value)` accepts `ERROR <nfsstat-or-name> <ceiling>` lines and stores them as `["ERROR", status_code, ceiling]`.
- `ConfigLine(name, value, comment, verifier=None)` stores one configurable value plus its parser and documentation string.
- `MetaConfig` deep-copies class `attrs` into each instance and replaces each `ConfigLine` with a Python property backed by `self.attrs[i].value`.
- `ServerConfig` contains server-wide settings such as `allow_null_data`, `tag_info`, `lease_time`, and `catch_ctrlc`, plus server owner, scope, and implementation identity data.
- `ServerPerClientConfig` holds session negotiation limits and behavior toggles such as request/response sizes, operation count, slot count, stateid handling, close-with-locks behavior, and debug state.
- `OpsConfigServer` builds one config line per `nfs_opnum4` operation, defaulting every operation to `ERROR 0 0`.
- `Actions` defines the `reboot` action config line.

## Control Flow
Class creation for config classes goes through `MetaConfig`, which consumes the declared `attrs` list, installs an `__init__` wrapper that deep-copies it, and creates properties with the same names as the config lines. Runtime reads and writes therefore look like normal attribute access while preserving comments and verifier behavior in `self.attrs`.

When a config pseudo-file is written and later closed by `ConfigObj` in `fs.py`, the raw non-comment line is assigned into `ConfigLine.value`. The property setter calls the verifier. Normal verifiers coerce to the stored type; `_action` raises `ConfigAction`; `_opline` parses operation fault-injection lines into structured lists. `ConfigObj.close` catches `ConfigAction` and dispatches actions such as server reboot.

## State And Persistence Behavior
The config objects are in-memory Python structures by default. Their values may be represented as file contents by `ConfigFS`, but the authoritative state is each `ConfigLine._value`. `MetaConfig` deep-copies class defaults per instance, preventing normal cross-client mutation for per-client configs. `ServerConfig.__init__` also creates process-specific owner data from `os.getpid()` and a fixed implementation timestamp.

## Dependencies And Integration Points
The module depends on generated NFSv4 constants/types, `nfs4lib.get_nfstime`, and `copy.deepcopy`. It is consumed by `fs.ConfigObj`/`ConfigFS`, by server code that reads limits and action flags, and by client test helpers that write `/config/ops/<operation>` or `/config/actions/reboot`.

## Risks And Edge Cases
- `_statcode` references `xdr.nfs4_const` even though the module imported `xdrdef.nfs4_const`; this typo can break symbolic status parsing.
- The metaclass declaration uses Python 2 `__metaclass__` syntax, which does not apply to classes under Python 3 without adaptation.
- `_opline` emits debug prints and has a print path using `len` rather than `len(l)`, reducing clarity during failures.
- `_opline` only supports `ERROR`; additional message types require verifier and server handling changes.
- `_valid_server_ops` and `_invalid_ops` are declared but not enforced in this file.
- Generated `OpsConfigServer.attrs` includes invalid operations despite comments saying some should not be set.

## Test Signals
Tests should verify text-to-type coercion for booleans/integers, operation error injection by numeric and symbolic status code, reboot action propagation through `ConfigObj.close`, independent per-client defaults, and session negotiation values reflected in `CREATE_SESSION` behavior. Python-version compatibility is a major signal for this file.
