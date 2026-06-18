# Research: sources/user-network-fs/impacket/impacket/system_errors.py

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009639`: lines 1-2124, `Docs/researches/chunks/subset-b-009639_research.md`
- `subset-b-009640`: lines 2125-4899, `Docs/researches/chunks/subset-b-009640_research.md`
- `subset-b-009641`: lines 4900-5526, `Docs/researches/chunks/subset-b-009641_research.md`

## Chunk Research

### subset-b-009639: lines 1-2124

# sources/user-network-fs/impacket/impacket/system_errors.py lines 1-2124

## Scope

This chunk covers the first 2,124 lines of `impacket/system_errors.py`. It starts the module header and the top-level `ERROR_MESSAGES` mapping, then continues through the first 2,105 entries of that mapping. The full source file continues beyond this chunk: the dictionary closes later at line 2771, and the module then exports one numeric constant per Windows system error code from line 2776 onward.

The assigned range ends inside the `ERROR_MESSAGES` literal at `0x000021c0` (`ERROR_DS_DISALLOWED_NC_REDIRECT`). The next line begins additional directory service and later DNS errors, so this chunk must be merged with later chunks before any final per-file conclusion about complete coverage.

## Purpose

`system_errors.py` is Impacket's central catalog for Win32/System error codes from Microsoft MS-ERREF. The header explicitly describes it as the shared source that other files should use for system error names and messages.

Within this chunk, the module provides integer error code lookup data for common Windows API, filesystem, network, service control, RPC, printer, WINS, PeerDist, WMI, cluster, transaction, Terminal Services, File Replication Service, and Active Directory/Directory Service conditions. Each entry maps a numeric error code to a tuple containing:

- the symbolic Windows error name, such as `ERROR_ACCESS_DENIED` or `RPC_S_SERVER_UNAVAILABLE`
- the human-readable message string used in exception formatting and diagnostics

The chunk starts at `ERROR_SUCCESS` (`0x00000000`) and reaches `ERROR_DS_DISALLOWED_NC_REDIRECT` (`0x000021c0`). The entries are ordered by ascending integer code, with gaps where MS-ERREF has no value or this generated table intentionally omits one.

## Important APIs, Types, And Data

The main data structure in this chunk is:

```python
ERROR_MESSAGES = {
    0x00000000: ("ERROR_SUCCESS", "The operation completed successfully."),
    ...
}
```

Important properties of this structure:

- Keys are Python integers written as fixed-width hexadecimal literals.
- Values are two-element tuples of strings: `(symbolic_name, verbose_message)`.
- The table is defined at import time and is globally mutable because it is an ordinary dictionary, although local code treats it as a constant.
- This chunk contributes 2,105 entries to the full mapping, covering codes from `0x0` through `0x21c0`.
- Names are not exported as individual constants in this assigned range; the separate `ERROR_FOO = 0x...` constant block starts after the dictionary in a later part of the file.

Representative groups covered by this range include:

- Basic DOS/Win32 filesystem and process errors: `ERROR_FILE_NOT_FOUND`, `ERROR_PATH_NOT_FOUND`, `ERROR_ACCESS_DENIED`, `ERROR_INVALID_HANDLE`, `ERROR_SHARING_VIOLATION`, `ERROR_MORE_DATA`.
- Network and logon errors: `ERROR_BAD_NETPATH`, `ERROR_NETNAME_DELETED`, `ERROR_NO_LOGON_SERVERS`, `ERROR_LOGON_FAILURE`, account and SID validation failures.
- Service Control Manager errors: `ERROR_SERVICE_DOES_NOT_EXIST`, `ERROR_SERVICE_DISABLED`, `ERROR_SERVICE_MARKED_FOR_DELETE`.
- Registry, tape/media, device, printer, and spooler errors.
- RPC and endpoint mapper errors: `RPC_S_INVALID_STRING_BINDING`, `RPC_S_SERVER_UNAVAILABLE`, `EPT_S_NOT_REGISTERED`, `RPC_X_BAD_STUB_DATA`.
- WINS, PeerDist, WMI, app container, media library, remote storage, reparse point, secure boot, and offload errors.
- Cluster service errors and Transactional NTFS/KTM errors.
- Terminal Services/RDP context errors.
- File Replication Service errors.
- The beginning and majority of Active Directory/Directory Service errors, including schema, naming, replication, FSMO, SPN, search, audit, and domain rename states.

## Control Flow

There are no functions, classes, conditionals, loops, imports, or runtime branching in this chunk. Importing the module executes the dictionary literal construction. All control flow happens in consumers that import this module and perform dictionary lookups.

The lookup pattern across Impacket is typically:

```python
if key in system_errors.ERROR_MESSAGES:
    error_msg_short = system_errors.ERROR_MESSAGES[key][0]
    error_msg_verbose = system_errors.ERROR_MESSAGES[key][1]
```

Several DCE/RPC modules use this pattern inside `DCERPCSessionError.__str__` implementations. Some consumers first check HRESULT or NTSTATUS tables, then fall back to `system_errors.ERROR_MESSAGES`, sometimes masking an HRESULT with `key & 0xffff` to obtain the embedded Win32 code.

This means the effective control-flow contract for this chunk is simple and data-driven: if an integer code is present, exception formatting can produce stable symbolic and verbose text; if absent, the caller normally emits an "unknown error code" path or checks another error table.

## State And Persistence Behavior

The chunk creates only in-process module state:

- `ERROR_MESSAGES` is allocated when `impacket.system_errors` is imported.
- There is no file, registry, network, cache, database, or credential persistence.
- The mapping is process-local and survives for the lifetime of the Python interpreter/module cache.
- Because it is mutable, accidental edits by runtime code would affect all later consumers in the same process. The observed codebase uses it read-only.

The messages are static source data copied from the error reference. They are not localized at runtime and do not query Windows APIs such as `FormatMessage`.

## Dependencies And Integration Points

This chunk has no direct imports. Its dependency is conceptual rather than executable: the entries must match MS-ERREF/Win32 system error semantics.

Integration points found elsewhere in the Impacket tree include:

- `impacket/dcerpc/v5/rprn.py`, `wkst.py`, `rrp.py`, `scmr.py`, `srvs.py`, `even6.py`, `dssp.py`, `bkrp.py`, `raa.py`, `rpch.py`, `nrpc.py`, and similar protocol modules import `system_errors` to format DCE/RPC exceptions.
- `impacket/dcerpc/v5/dhcpm.py` uses `system_errors.ERROR_MESSAGES` in combination with DHCP-specific messages and also uses constants such as `ERROR_MORE_DATA` from the later constant block to drive pagination loops.
- `impacket/dcerpc/v5/drsuapi.py` and `tsch.py` use the low 16 bits of a returned code (`key & 0xffff`) to resolve embedded system errors after checking HRESULT messages.
- Example tools such as `examples/reg.py`, `examples/regsecrets.py`, and `examples/secretsdump.py` import system error constants or use `ERROR_MESSAGES` to produce user-visible diagnostics.
- `impacket/smbserver.py` imports constants such as `ERROR_INVALID_LEVEL` from the later half of this same module.

For the lines in this chunk specifically, the message mapping matters most for exception text. The individual constant names mentioned in this chunk are not bound until the later constant block, so a consumer doing `from impacket.system_errors import ERROR_MORE_DATA` depends on another chunk of this file, not on lines 1-2124 alone.

## Risks And Edge Cases

Important maintenance risks in this chunk:

- The data is hand-maintained or generated static source. A typo in a key, symbolic name, or message will silently produce misleading diagnostics rather than a runtime error.
- Missing codes are indistinguishable from intentionally unsupported codes to consumers; most callers simply report an unknown error.
- Some messages include Windows insertion placeholders such as `%1`, `%2`, `%s`, and URLs. Impacket returns them verbatim rather than performing Windows message formatting.
- The dictionary is mutable. Any runtime mutation changes process-wide error formatting and could create hard-to-track diagnostics differences.
- The table contains protocol-specific ranges adjacent to each other. Adding or sorting entries manually can accidentally place a code in the wrong range or duplicate a code; Python would keep only the last duplicate key in the literal.
- This chunk ends mid-dictionary. A syntax or merge error around chunk boundaries would prevent importing the entire module, not just later entries.
- Consumers that mask HRESULTs to 16 bits rely on the system error code being present in this table. If a relevant low-word code is missing or incorrectly named, DRSUAPI/Task Scheduler-style exceptions degrade to generic output.

Potential correctness checks should focus on the table as data, not on algorithmic behavior.

## Test Signals

Useful test signals for this chunk include:

- Import smoke test: `python -c "from impacket import system_errors; print(system_errors.ERROR_MESSAGES[5])"` should import without syntax errors and return the `ERROR_ACCESS_DENIED` tuple.
- Shape invariant: every entry in `ERROR_MESSAGES` should have an integer key and a two-string tuple value.
- Known-value checks for high-traffic codes used by Impacket callers, including `0x00000005` (`ERROR_ACCESS_DENIED`), `0x0000007a` (`ERROR_INSUFFICIENT_BUFFER`), `0x000000ea` (`ERROR_MORE_DATA`), `0x000006ba` (`RPC_S_SERVER_UNAVAILABLE`), `0x0000052e` (`ERROR_LOGON_FAILURE`), and `0x0000203a` (`ERROR_DS_SERVER_DOWN`).
- Consumer formatting tests can instantiate or trigger DCE/RPC session errors in modules that use `system_errors.ERROR_MESSAGES` and assert that known system codes produce symbolic plus verbose output.
- Static validation against MS-ERREF or a generated authoritative source would catch stale, missing, duplicated, or mistranscribed codes.
- Because the module later exports numeric constants mirroring these names, a full-file reconciliation test should verify that each constant value agrees with the corresponding `ERROR_MESSAGES` key once all chunks are merged.

### subset-b-009640: lines 2125-4899

# sources/user-network-fs/impacket/impacket/system_errors.py lines 2125-4899

## Scope

This chunk covers the tail of Impacket's `ERROR_MESSAGES` table and the first large block of module-level numeric aliases for Windows system error codes.

The assigned range starts at line 2125 inside the `ERROR_MESSAGES` dictionary with Active Directory Lightweight Directory Services/domain-join errors, continues through DNS, Winsock, IPsec, side-by-side assembly, event log, MUI, monitor configuration, package/app model/state repository, and Store licensing entries, and reaches the dictionary close at line 2771. It then resumes at line 2776 with exported integer constants beginning at `ERROR_SUCCESS = 0x00000000` and ends at line 4899 with `DNS_ERROR_RCODE_BADTIME = 0x0000233a`. Later DNS constants and later system-error families continue after this chunk.

Within this exact range there are 646 dictionary entries and 2,122 constant assignments.

## Purpose

`system_errors.py` is Impacket's local copy of Windows system error metadata from `[MS-ERREF]`. It provides two related interfaces:

- `ERROR_MESSAGES`: maps a numeric Win32/system error code to a pair of `(symbolic_name, human_readable_message)`.
- Module-level constants: expose symbolic names as integer values so protocol code and tests can compare status values without hard-coded literals.

The dictionary portion in this chunk is used to turn returned RPC/DCE/RPC and service status codes into useful exception strings. The constant portion is used by callers that need to compare protocol return values, set default pagination status, or assert expected status codes.

## Important APIs, Types, And Data

There are no functions or classes in this range. The important API surface is import-time global data:

- `ERROR_MESSAGES` entries have integer keys and 2-tuples of strings. Consumers expect index `0` to be the short symbolic name and index `1` to be the verbose message.
- The dictionary slice begins with `0x000021c1: ("ERROR_DS_HIGH_ADLDS_FFL", ...)` and ends with `0x00003df6: ("STORE_ERROR_UNLICENSED_USER", ...)`.
- Constant aliases begin at `ERROR_SUCCESS = 0x00000000` and, in this chunk, continue through `DNS_ERROR_RCODE_BADTIME = 0x0000233a`.
- The dictionary and constants intentionally duplicate names and values. For example, `ERROR_DS_HIGH_ADLDS_FFL` appears as a dictionary payload in the first half and as a numeric constant near this chunk's end.

Major error families represented in the dictionary slice include:

- Active Directory and AD LDS completion/failure codes around `0x21c1-0x21c6`.
- DNS server, DNSSEC, zone, record, update, and directory-partition status codes around `0x2329-0x26b2`.
- Winsock `WSA*` socket and resolver errors around `0x2714-0x2afc`.
- IPsec/IKE, filter, and policy negotiation errors around `0x32c8-0x3654`.
- Side-by-side activation/context/XML/manifest errors around `0x36b0-0x371d`.
- Event log and event subscription/query errors around `0x3a98-0x3abf`.
- MUI/resource-loading errors around `0x3afc-0x3b65`.
- Monitor configuration, graphics, and MCA status codes around `0x3b60-0x3b92`.
- Windows installer, package deployment, app model, state repository, and Store licensing errors around `0x3cf0-0x3df6`.

The constant slice restarts from low-numbered common system errors and reaches partway into the DNS family. It therefore overlaps earlier dictionary entries from the full file as well as the dictionary entries in this chunk.

## Control Flow

The code has only module initialization flow:

1. Python imports `impacket.system_errors`.
2. The interpreter builds the `ERROR_MESSAGES` dictionary from literal entries.
3. It binds every uppercase error-name constant to its numeric integer value.
4. Downstream modules read the dictionary or constants directly.

Exception formatting in consuming modules usually follows the same pattern: check whether a returned integer status exists in `system_errors.ERROR_MESSAGES`, pull the short and verbose strings, and interpolate them into a protocol-specific `SessionError` string. Constant consumers import names such as `ERROR_MORE_DATA`, `ERROR_NO_MORE_ITEMS`, `ERROR_INVALID_LEVEL`, or `ERROR_NOT_SUPPORTED` and compare them directly to returned status values.

## State And Persistence Behavior

This chunk creates process-local immutable-by-convention metadata. It does not perform I/O, open sockets, write files, cache runtime results, or persist anything outside the Python process.

The state risk is global mutability: `ERROR_MESSAGES` is a normal dictionary, and constants are normal module globals. Impacket code treats them as read-only, but accidental mutation after import would affect all later error formatting in the same interpreter. There is no defensive copy or frozen mapping.

Import cost is proportional to the full generated table. This range alone contributes thousands of literal objects, but lookup behavior remains constant-time dictionary access for messages and direct global-name access for constants.

## Dependencies And Integration Points

This file has no imports in the inspected range and no external runtime dependencies beyond Python's literal evaluation. Its semantic dependency is Microsoft's `[MS-ERREF]` error-code catalog; accuracy depends on keeping codes, names, and messages aligned with that source.

Observed integration points in the Impacket tree include:

- `impacket/dcerpc/v5/rprn.py`, `rpch.py`, `rrp.py`, `tsts.py`, `srvs.py`, `wkst.py`, and `dhcpm.py`: consult `system_errors.ERROR_MESSAGES` when formatting DCE/RPC service exceptions.
- `impacket/dcerpc/v5/drsuapi.py`: falls back to `system_errors.ERROR_MESSAGES[key & 0xffff]` after HRESULT lookup, making low-word correctness important for directory replication errors.
- `impacket/dcerpc/v5/rrp.py` and `dhcpm.py`: compare returned status values against constants such as `ERROR_MORE_DATA` for enumeration loops.
- `examples/reg.py`: imports `ERROR_NO_MORE_ITEMS` for registry enumeration termination.
- `impacket/smbserver.py`: imports `ERROR_INVALID_LEVEL`.
- `tests/dcerpc/test_tsch.py`: imports `ERROR_NOT_SUPPORTED` for expected scheduler behavior.

The chunk's DNS constants may also be used by callers outside the repository through the public `impacket.system_errors` module API.

## Risks And Maintenance Notes

- The table is mechanical and duplicate-heavy. A typo in either the dictionary entry or the constant alias can create confusing disagreement between formatted messages and numeric comparisons.
- Several consumers assume `ERROR_MESSAGES[key]` is exactly a 2-tuple. Changing the value shape would break exception formatting.
- `drsuapi.py` masks HRESULT-style values with `0xffff` before lookup, so low-word collisions or missing low-word system errors can produce misleading messages.
- The chunk boundary is not an API boundary. It starts inside the dictionary and ends inside the DNS constant family; whole-file conclusions must be reconciled with adjacent chunks.
- Because this module has no validation logic, duplicate values, stale messages, or missing aliases are not detected at import time.
- Messages are user-visible in exceptions. Updating from `[MS-ERREF]` can change test expectations or downstream tooling that matches exact strings.
- The dictionary is mutable at runtime. Tests or callers that monkey-patch it can affect unrelated protocol modules in the same process.

## Test Signals

Useful tests for this data should verify:

- `impacket.system_errors` imports successfully and `ERROR_MESSAGES` is populated.
- Representative dictionary entries from this chunk resolve correctly, such as `0x00002329` to `DNS_ERROR_RCODE_FORMAT_ERROR`, `0x00002746` to `WSAECONNRESET`, and `0x00003df6` to `STORE_ERROR_UNLICENSED_USER`.
- Representative constants in this chunk have the expected integer values, including `ERROR_SUCCESS == 0x00000000`, `ERROR_MORE_DATA == 0x000000ea`, `ERROR_DS_HIGH_ADLDS_FFL == 0x000021c1`, and `DNS_ERROR_RCODE_BADTIME == 0x0000233a`.
- Protocol exception classes that use `system_errors.ERROR_MESSAGES` include both symbolic and verbose strings for known system errors and fall back cleanly for unknown codes.
- Enumeration loops that compare against constants such as `ERROR_MORE_DATA` and `ERROR_NO_MORE_ITEMS` still terminate correctly.

For maintenance, a generated consistency check would be valuable: every constant name/value pair that has a corresponding `ERROR_MESSAGES` entry should agree with the dictionary's symbolic name for that numeric value, allowing for intentional aliases only when documented.

### subset-b-009641: lines 4900-5526

# sources/user-network-fs/impacket/impacket/system_errors.py lines 4900-5526

## Scope

This chunk covers the final block of `system_errors.py`, from `DNS_ERROR_KEYMASTER_REQUIRED` through `STORE_ERROR_UNLICENSED_USER`. It is the tail of the module-level symbolic constants that mirror the large `ERROR_MESSAGES` dictionary defined earlier in the same file. The range starts in the DNS error-code family and then covers Winsock, IPsec/IKE, side-by-side assembly, Windows Event Log, event collector, MUI/MRM, monitor configuration, GPIO, runlevel, package deployment, app model, state repository, API availability, and Store licensing constants.

The chunk contains no classes, functions, imports, or executable logic beyond Python assignment statements evaluated at import time.

## Purpose

`system_errors.py` centralizes Windows system error values from MS-ERREF for Impacket. Earlier in the file, `ERROR_MESSAGES` maps numeric Windows error codes to `(symbol, description)` tuples for rendering RPC and protocol exceptions. The constant section gives callers stable Python names for the same numeric values, so code can compare return codes without copying integers.

This chunk extends that public constant namespace for later Windows subsystems:

- DNSSEC, DNS zone, DNS record, and DNS directory-partition errors in the `0x238d` through `0x26b2` ranges.
- Winsock and Winsock QoS errors in the `0x2714` through `0x2b19` ranges.
- IPsec policy, IKE negotiation, packet-processing, and DOS protection errors in the `0x32c8` through `0x366c` ranges.
- Side-by-side assembly and XML activation context errors in the `0x36b0` through `0x371e` ranges.
- Windows Event Log and Event Collector errors in the `0x3a98` through `0x3aed` ranges.
- Resource localization, monitor configuration, GPIO, runlevel, package deployment, app model, state-store, API, and Store licensing errors in the `0x3afc` through `0x3df6` ranges.

## Important APIs And Data

The only API surface in this range is a set of module globals. They are imported directly by callers that need symbolic constants and are also available through `impacket.system_errors` when modules import the whole namespace.

Representative constants include:

- `DNS_ERROR_DNSSEC_IS_DISABLED`, `DNS_ERROR_ZONE_DOES_NOT_EXIST`, `DNS_ERROR_RECORD_ALREADY_EXISTS`, and `DNS_ERROR_DP_FSMO_ERROR` for DNS management/status handling.
- `WSAEWOULDBLOCK`, `WSAECONNRESET`, `WSAETIMEDOUT`, `WSAHOST_NOT_FOUND`, `WSANO_DATA`, and `WSA_IPSEC_NAME_POLICY_ERROR` for socket and resolver failures.
- `ERROR_IPSEC_QM_POLICY_NOT_FOUND`, `ERROR_IPSEC_IKE_AUTH_FAIL`, `ERROR_IPSEC_IKE_NEGOTIATION_DISABLED`, `ERROR_IPSEC_BAD_SPI`, and `ERROR_IPSEC_DOSP_NOT_INSTALLED` for IPsec policy, IKE, and packet-layer reporting.
- `ERROR_SXS_MANIFEST_PARSE_ERROR`, `ERROR_SXS_XML_E_MISSINGQUOTE`, `ERROR_SXS_COMPONENT_STORE_CORRUPT`, and `ERROR_SXS_FILE_HASH_MISSING` for side-by-side assembly manifest and component-store issues.
- `ERROR_EVT_INVALID_QUERY`, `ERROR_EVT_CHANNEL_NOT_FOUND`, `ERROR_EVT_MESSAGE_NOT_FOUND`, and `ERROR_EC_CRED_NOT_FOUND` for Event Log/Event Collector protocol surfaces.
- `ERROR_MUI_INVALID_LOCALE_NAME`, `ERROR_MRM_NO_CANDIDATE`, `ERROR_MCA_UNSUPPORTED_MCCS_VERSION`, `ERROR_GPIO_OPERATION_DENIED`, `ERROR_INSTALL_PACKAGE_NOT_FOUND`, `APPMODEL_ERROR_NO_PACKAGE`, `ERROR_STATE_WRITE_SETTING_FAILED`, `ERROR_API_UNAVAILABLE`, and `STORE_ERROR_UNLICENSED_USER` for newer Windows platform subsystems.

There are no custom types. Every binding is an `int` literal written in hexadecimal to preserve visual alignment with Windows documentation.

## Control Flow

Control flow is limited to import-time execution:

1. Python evaluates the earlier `ERROR_MESSAGES` dictionary.
2. Python evaluates each constant assignment in order.
3. The module namespace then exposes both lookup table data and named integer constants to importers.

No branches, loops, error handling, lazy initialization, or runtime mutation occur in this chunk. The ordering is still meaningful for maintainability because constants follow the numeric ordering and family grouping from MS-ERREF.

## State And Persistence Behavior

The state introduced here is immutable-by-convention process memory. Each symbol is bound once when the module is imported. Python does not enforce immutability for module globals, but the file treats these names as constants and no local code mutates them.

There is no persistence, I/O, cache, environment dependency, or per-instance state. Re-imports use Python's normal module cache, so the assignments are executed once per interpreter load unless the module is explicitly reloaded.

## Dependencies And Integration Points

The constants depend semantically on Microsoft MS-ERREF numeric assignments. The file header states that `system_errors.py` is intended to be the central source for SYSTEM errors, and many Impacket DCE/RPC modules integrate through it.

Observed integration patterns include:

- RPC session exception renderers, such as `dcerpc/v5/rpch.py`, `rprn.py`, `rrp.py`, `scmr.py`, `srvs.py`, `wkst.py`, `even6.py`, and related modules, check `system_errors.ERROR_MESSAGES` to turn numeric return codes into symbolic names and descriptions.
- Some protocol modules compare direct constants from this module, for example registry and service helpers checking `ERROR_MORE_DATA`, `ERROR_INSUFFICIENT_BUFFER`, or similar system status values.
- `dcerpc/v5/drsuapi.py` and `dcerpc/v5/tsch.py` mask HRESULT-like values with `0xffff` before consulting `ERROR_MESSAGES`, so constants in this file also matter when only the low 16 bits carry a system error.
- Examples and tests, including secrets dumping paths, search rendered exception text such as `ERROR_DS_DRA_BAD_DN`, demonstrating that consistency between `ERROR_MESSAGES` and constants affects user-visible diagnostics.

This specific chunk's later subsystem constants may be used by current or future modules that bind to DNS, Event Log, IPsec, package deployment, or app model interfaces. Even when direct constant imports are absent today, the matching `ERROR_MESSAGES` entries allow exception formatting for these code ranges.

## Risks And Maintenance Notes

- Numeric drift is the primary risk. A wrong hex value can make equality checks fail silently or render an unrelated Windows error name.
- The file duplicates information in two forms: `ERROR_MESSAGES` entries and module-level constants. Additions or corrections should keep the integer-to-name mapping and the named constant aligned.
- This chunk contains only names and values, so unit tests that import the module will catch syntax errors but not semantic mismatches against MS-ERREF.
- Direct `from impacket.system_errors import NAME` users rely on these symbols remaining stable. Renaming or removing constants is a compatibility break even if `ERROR_MESSAGES` still contains the code.
- These are Win32/system error values, not NTSTATUS or HRESULT values. Callers need to use `nt_errors` or `hresult_errors` where appropriate, or apply the same masking pattern used by DRSUAPI/TSCH only when the protocol returns a wrapped system code.
- The module has no generated-code marker. Because the list is long and repetitive, manual edits are easy to misalign; review should compare against authoritative MS-ERREF ranges rather than relying on nearby visual patterns alone.

## Test Signals

Useful verification for this chunk is mostly static and integration-oriented:

- `python -m py_compile sources/user-network-fs/impacket/impacket/system_errors.py` confirms the large dictionary and constant tail remain syntactically valid.
- Import smoke tests can assert representative bindings, for example `DNS_ERROR_KEYMASTER_REQUIRED == 0x238d`, `WSAECONNRESET == 0x2746`, `ERROR_IPSEC_IKE_AUTH_FAIL == 0x35e9`, `ERROR_SXS_COMPONENT_STORE_CORRUPT == 0x3712`, `ERROR_EVT_INVALID_QUERY == 0x3a99`, and `STORE_ERROR_UNLICENSED_USER == 0x3df6`.
- Consistency tests can check that every constant in this range has the same numeric key/name pair in `ERROR_MESSAGES` where the message table includes that code.
- Existing DCE/RPC exception tests indirectly validate lookup behavior when a returned system error code is present in `ERROR_MESSAGES`; targeted tests for Event Log or DNS RPC errors would give stronger coverage for constants in this range.
- Static analysis should flag duplicate constant values only when MS-ERREF does not intentionally alias names. In this chunk, several families are contiguous ranges, so gaps are expected and should not automatically fail validation.
