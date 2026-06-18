# Research: sources/user-network-fs/impacket/impacket/hresult_errors.py

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009625`: lines 1-2196, `Docs/researches/chunks/subset-b-009625_research.md`
- `subset-b-009626`: lines 2197-5001, `Docs/researches/chunks/subset-b-009626_research.md`
- `subset-b-009627`: lines 5002-5877, `Docs/researches/chunks/subset-b-009627_research.md`

## Chunk Research

### subset-b-009625: lines 1-2196

# `sources/user-network-fs/impacket/impacket/hresult_errors.py` lines 1-2196

## Purpose

This chunk begins Impacket's shared HRESULT lookup table. The module header identifies the data as HRESULT errors from Microsoft `[MS-ERREF]` and notes the intended direction that protocol modules should centralize HRESULT decoding through this file. Lines 1-2196 define the start of one module-level constant, `ERROR_MESSAGES`, mapping integer HRESULT values to `(symbolic_name, human_message)` tuples.

The chunk is data-only. It contains no classes, functions, imports, branching logic, I/O, or runtime initialization beyond constructing the Python dictionary at import time. The covered range starts at the copyright/header block and line 19 dictionary assignment, then includes 2,177 HRESULT entries through `0xC00D11DF` / `NS_E_WMP_MULTIPLE_ERROR_IN_PLAYLIST`. The dictionary continues after this chunk, so this research note covers only the first slice of the table.

## Important APIs, Types, and Data Shape

`ERROR_MESSAGES` is the only API in this chunk. Its contract is:

```python
ERROR_MESSAGES = {
    0xHRESULT: ("ERROR_SYMBOL", "Human-readable explanation"),
}
```

Consumers use integer dictionary lookups and then index tuple element `0` for the short symbolic name and tuple element `1` for the verbose description. The data is keyed by Python integers written as hexadecimal literals, not strings. Messages are plain strings and sometimes preserve Windows placeholder syntax such as `%1`, `%2`, `%s`, `%d`, and formatting details from the source specifications.

The table is broad rather than protocol-specific. This chunk includes success, informational, warning, and failure HRESULT families, including:

- Structured storage, OLE, COM, DCOM, RPC, Dispatch, type library, clipboard, moniker, cache, event, scheduler, transaction, and COM+ results.
- Security and crypto families such as SSPI/Kerberos-adjacent `SEC_*`, CryptoAPI `CRYPT_*`, certificate/trust `CERT_*` and `TRUST_*`, smart card `SCARD_*`, TPM/TBS/TPMAPI, and ASN.1/OSS errors.
- Windows subsystem families for filter manager, graphics/display, Performance Logs and Alerts, BitLocker/FVE, Windows Filtering Platform, NDIS, distributed link tracking, and auditing.
- Windows Media/NetShow `NS_*` and `NS_E_WMP_*` errors, which dominate the end of the chunk and continue past line 2196.

## Control Flow

There is no explicit control flow in the chunk. Importing the module evaluates the dictionary literal once and binds it to `ERROR_MESSAGES`. All later behavior is driven by external consumers checking membership in the dictionary and formatting errors from tuple values.

The main implicit flow is lookup-oriented:

1. A protocol layer receives or constructs a numeric HRESULT/status value.
2. It checks `if code in hresult_errors.ERROR_MESSAGES`.
3. It extracts `ERROR_MESSAGES[code][0]` and `ERROR_MESSAGES[code][1]`.
4. It formats a `SessionError` or logging message with the symbolic and verbose text.

Unknown codes are not handled by this file; callers decide their own fallback text.

## State and Persistence Behavior

The chunk creates process-local immutable-by-convention module state. `ERROR_MESSAGES` is a mutable dictionary, but this file never mutates it after construction and performs no persistence. There is no disk, network, registry, database, environment, or cache interaction. Because the table is built at import time, its runtime cost is proportional to importing and allocating the large dictionary, and its memory footprint is always paid by processes importing `impacket.hresult_errors`.

The data is deterministic and has no dependency on platform state. A consumer can safely use it offline and in tests without a Windows host.

## Dependencies

This chunk has no imports and no third-party dependencies. The only external dependency is semantic: the table mirrors Microsoft HRESULT names and descriptions from `[MS-ERREF]`. Since the module does not generate or validate these entries dynamically, correctness depends on the literal table staying synchronized with the upstream specification and with any protocol modules that expect a given HRESULT to be present.

Sibling modules use the same pattern for other error namespaces, including `nt_errors.py`, `system_errors.py`, and `mapi_constants.py`. Those files are separate dictionaries rather than dependencies of this file.

## Integration Points

Several Impacket DCE/RPC and DCOM modules import this table directly for exception rendering. Local references show direct use in modules such as:

- `impacket/dcerpc/v5/tsch.py`, `atsvc.py`, `sasec.py`, `gkdi.py`, `drsuapi.py`, `iphlp.py`, `nspi.py`, `oxabref.py`, and `icpr.py`.
- DCOM modules including `dcomrt.py`, `dcom/wmi.py`, `dcom/oaut.py`, `dcom/scmp.py`, `dcom/vds.py`, and `dcom/comev.py`.
- `impacket/dcerpc/v5/rpcrt.py`, which checks `hresult_errors.ERROR_MESSAGES` while decoding RPC status/fault values.

The integration contract is narrow but widely shared: entries must remain indexed by exact integer HRESULT and values must remain two-element tuples. If the tuple shape changes, many `SessionError.__str__` implementations that do `ERROR_MESSAGES[key][0]` and `[1]` would break.

## Risks and Edge Cases

- Coverage gaps produce weaker diagnostics. Unknown HRESULTs fall through to caller-specific generic formatting, so missing or incorrect entries reduce operator clarity rather than usually breaking protocol behavior.
- The table includes both success/informational values and failures. Callers should not infer failure solely from presence in this dictionary; the high bits of the HRESULT or protocol semantics must still drive success/error decisions.
- Some messages include Windows formatting placeholders. Callers currently display them literally; adding interpolation would require knowing the original parameter context and could introduce formatting errors.
- The dictionary is mutable and globally shared. Accidental runtime mutation by another module would affect all later error formatting in the process.
- Literal transcription errors are plausible in a file this large. A wrong integer key can silently map an HRESULT to the wrong message, while duplicate keys later in the full dictionary would overwrite earlier entries at import time.
- Chunk boundary risk: line 2196 ends in the middle of the full `ERROR_MESSAGES` literal, immediately before additional Windows Media entries. A final per-file report must reconcile this chunk with later chunks before drawing whole-file conclusions.

## Test Signals

Useful checks for this chunk are mostly structural and integration-focused:

- Import or compile the module to catch malformed dictionary syntax in the full file, since this chunk alone does not include the dictionary close.
- Assert representative lookups from this range, for example `0x80004005 -> E_FAIL`, `0x80070005 -> E_ACCESSDENIED`, `0x8009030C -> SEC_E_LOGON_DENIED`, `0x8010002E -> SCARD_E_NO_READERS_AVAILABLE`, `0x80310000 -> FVE_E_LOCKED_VOLUME`, and `0xC00D11DF -> NS_E_WMP_MULTIPLE_ERROR_IN_PLAYLIST`.
- Exercise a consumer `SessionError` path from modules such as `tsch`, `dcomrt`, or `rpcrt` and verify the formatted string includes the symbolic HRESULT name.
- Add a shape invariant test that all covered entries are `int -> tuple[str, str]` with tuple length two.
- For synchronization work against `[MS-ERREF]`, compare keys and symbols rather than verbose text only, because message wording can be long and placeholder-heavy.

### subset-b-009626: lines 2197-5001

# sources/user-network-fs/impacket/impacket/hresult_errors.py lines 2197-5001

## Scope

This chunk covers the latter part of Impacket's HRESULT error catalog. It starts inside the `ERROR_MESSAGES` dictionary at the Windows Media Player / Windows Media namespace error range, closes that dictionary at line 2947, and then begins the module-level `# Error Codes` constant aliases from the first HRESULT in the file through `NS_E_WMP_CONVERT_PLUGIN_UNKNOWN_FILE_OWNER`.

The range contains data definitions only: no functions, classes, imports, or executable control-flow branches beyond Python module initialization of a dictionary and integer constants. In this chunk, the source defines 750 `ERROR_MESSAGES` entries and 2,051 integer constant aliases.

## Purpose

`hresult_errors.py` centralizes HRESULT names and human-readable descriptions sourced from Microsoft's MS-ERREF catalog. Impacket uses it to turn numeric RPC/DCOM/HRESULT status values into useful exception messages while also exposing named constants for protocol stubs and callers that need symbolic HRESULT values.

Within this specific chunk, the dictionary entries mainly cover:

- Windows Media Player, media library, DRM, CD/DVD burning, sync, codec, playlist, URL, caching, and namespace failures in the `0xC00D11E0` through `0xC00D2F0B` ranges.
- Media Foundation transform, ASF parsing, streaming, proxy, device, and quality-of-service errors in the `0xC00D36xx` and related ranges.
- Windows graphics/display HRESULTs in the `0xC02620xx` through `0xC02625E0` ranges, including VidPN topology, monitor, OPM/PVP, DDC/CI, and MCA failures.

The constant section then restarts from the beginning of the full file's HRESULT catalog, exposing symbolic names such as `STG_S_CONVERTED`, COM/OLE/Task Scheduler/security success codes, many failure codes, and the early-to-mid Windows Media constants up to `NS_E_WMP_CONVERT_PLUGIN_UNKNOWN_FILE_OWNER`.

## Important APIs, Types, And Data

The primary API is the module-level `ERROR_MESSAGES` mapping:

- keys are integer HRESULT values, written as hexadecimal literals;
- values are two-tuples of `(symbolic_name, descriptive_message)`;
- callers perform direct membership tests and index lookups, for example `if key in hresult_errors.ERROR_MESSAGES`.

The second API surface is the flat set of module constants:

- each constant binds a symbolic HRESULT name to the corresponding integer value;
- the constants duplicate names already present as the first element of `ERROR_MESSAGES` entries;
- the chunk begins this alias table at `STG_S_CONVERTED = 0x00030200` and ends at `NS_E_WMP_CONVERT_PLUGIN_UNKNOWN_FILE_OWNER = 0xC00D115E`;
- later chunks continue the remaining aliases after this line.

There are no custom types. The data shape is deliberately simple so protocol modules can import either the whole `hresult_errors` module for lookup or individual constants by name.

## Control Flow

At import time Python evaluates the full dictionary literal and then evaluates each constant assignment in order. There is no runtime branching, lazy loading, normalization, or generation step in this source file.

Consumer-side control flow is outside this file but follows a common pattern:

1. Receive or decode a numeric HRESULT/status value from an RPC, DCOM, certificate, directory, or protocol response.
2. Check whether that integer is present in `hresult_errors.ERROR_MESSAGES`.
3. If present, use tuple element `0` as the short symbolic name and tuple element `1` as the verbose explanation.
4. If absent, fall back to a generic `unknown error code` message, another catalog such as `system_errors` or `mapi_constants`, or a low-word system-error lookup depending on the protocol module.

Because this chunk is split across a larger file, one boundary detail matters for reconciliation: line 2197 is not the start of `ERROR_MESSAGES`; it is a continuation of a dictionary that began at the top of the file. The dictionary itself closes in this chunk, and the constant alias table starts immediately afterward.

## State And Persistence Behavior

The module has no persistence behavior. Importing it creates process-local immutable-by-convention Python objects:

- `ERROR_MESSAGES`, a mutable dictionary that callers treat as a read-only catalog;
- many integer globals representing HRESULT constants.

No files, sockets, registry entries, caches, environment variables, or network resources are read or written by this chunk. The only durable state is the source text itself. If a consumer mutates `ERROR_MESSAGES` at runtime, that mutation is process-local and affects later lookups in the same interpreter, but the module does not intentionally provide mutation APIs.

## Dependencies And Integration Points

This file has no imports and no external runtime dependencies. Its integration points are the Impacket modules that import `hresult_errors` to format exceptions or protocol errors. Relevant examples in this source tree include:

- `impacket/dcerpc/v5/dcomrt.py`, where `DCERPCSessionError` uses `hresult_errors.ERROR_MESSAGES` for DCOM HRESULT messages.
- `impacket/dcerpc/v5/rpcrt.py`, where RPC fault/status formatting consults the HRESULT catalog when the status code matches.
- `impacket/dcerpc/v5/iphlp.py`, `gkdi.py`, `atsvc.py`, `sasec.py`, `drsuapi.py`, `tsch.py`, and `icpr.py`, which use the catalog in protocol-specific `DCERPCSessionError` implementations.
- DCOM helper modules under `impacket/dcerpc/v5/dcom/`, including `scmp.py`, `wmi.py`, `comev.py`, `vds.py`, and `oaut.py`, which use this table for COM-style error reporting.
- Exchange/MAPI-adjacent modules such as `nspi.py` and `oxabref.py`, which first try MAPI-specific messages and then fall back to HRESULT messages.

The constants are integration glue for code that needs to compare against named HRESULTs instead of magic numbers. This chunk's alias table covers storage, COM, scheduler, security, cryptography, TPM, UI, network, Windows Update, media, and early Windows Media namespaces up to the `0xC00D115E` range.

## Risks And Edge Cases

- The catalog is duplicated: each code appears once in `ERROR_MESSAGES` and again as a module constant. A manual update can accidentally change one representation without the other.
- Import cost and memory usage are proportional to the full catalog size. This is acceptable for exception formatting but should be considered if imported on hot startup paths.
- `ERROR_MESSAGES` is mutable. There is no defensive wrapper preventing accidental caller-side modification.
- The lookup contract assumes callers pass unsigned HRESULT integers matching the literal values. Signed 32-bit interpretations, low-word Win32 codes, or NTSTATUS values will not match unless the consumer normalizes them or falls back to another catalog.
- Several protocol modules use different fallback orders. For example, some check HRESULTs before system errors, while others check MAPI or low-word system errors first. A shared numeric value can therefore format differently depending on the caller.
- The chunk boundary splits the file's generated-style data: this range starts mid-dictionary and ends mid-constant table. Any final per-file report should merge this chunk with adjacent chunks before making whole-file completeness claims.
- Messages are copied from an external specification and can become stale if MS-ERREF adds, renames, or revises HRESULT descriptions.

## Test Signals

Useful validation for this chunk is mostly structural and integration-oriented:

- `python3 -m py_compile sources/user-network-fs/impacket/impacket/hresult_errors.py` should succeed, proving the large literal and constant assignments are syntactically valid.
- Importing `impacket.hresult_errors` should expose `ERROR_MESSAGES[0xC00D11E0] == ("NS_E_WMP_IMAPI2_ERASE_FAIL", ...)` and constant `NS_E_WMP_CONVERT_PLUGIN_UNKNOWN_FILE_OWNER == 0xC00D115E`.
- A consistency check can verify that each dictionary entry's symbolic name has a matching module global with the same integer value once the full file is loaded.
- Exception-formatting tests for DCOM/RPC protocol modules should assert that known HRESULTs render the symbolic short name and verbose message instead of generic unknown-error text.
- Fallback-path tests should cover an unknown HRESULT, a low-word Win32 error, and a MAPI-specific value to ensure this catalog integrates correctly with `system_errors`, `nt_errors`, and `mapi_constants`.

### subset-b-009627: lines 5002-5877

# sources/user-network-fs/impacket/impacket/hresult_errors.py lines 5002-5877

## Purpose

This chunk is the tail of Impacket's HRESULT catalog. It defines module-level symbolic constants for Windows error/status values from the `[MS-ERREF]` HRESULT namespace, starting in the Windows Media/DVD and portable-device range and ending at the last graphics/monitor constant in the file.

The file has two related surfaces:

- `ERROR_MESSAGES`, defined earlier in the file, maps integer HRESULT values to `(symbol, message)` tuples for diagnostic lookup.
- The flat constants section, which starts after `ERROR_MESSAGES`, exposes names such as `NS_E_WMP_ACCESS_DENIED` and `ERROR_GRAPHICS_INVALID_VIDPN_TOPOLOGY` as importable integer aliases.

Lines 5002-5877 are entirely in the second surface. They do not add lookup logic or messages, but they make the late `[MS-ERREF]` symbols available to code that prefers named constants over raw hex values.

## High-Level Structure

- Lines 5002-5034: Continues Windows Media Player conversion, DVD playback, copy-protection, CD burner, PDA, and IMAPI synchronization constants, beginning with `NS_E_DVD_DISC_COPY_PROTECT_OUTPUT_NS = 0xC00D1160`.
- Lines 5035-5146: Defines Windows Media Player, WMDM, codec, DRM, network, CD, sync wizard, background-download, cURL helper, subscription/content-partner, namespace, cache, publishing point, playlist, datapath, server plugin, logging, and capture/encoding constants.
- Lines 5147-5439: Defines Windows Media Encoder profile, input, device-control, audio/video format, multipass, timecode, and source-group validation constants, then enters a large DRM block beginning at `NS_E_DRM_INVALID_APPLICATION = 0xC00D2711`.
- Lines 5440-5635: Continues DRM store, license, individualization, backup/restore, migration, certificate, proximity, output-protection, setup, and streaming/network-protocol constants.
- Lines 5636-5660: Defines playlist termination and metadata/property-query constants such as `NS_E_PROPERTY_NOT_FOUND`, `NS_E_METADATA_FORMAT_NOT_SUPPORTED`, and `NS_E_METADATA_CANNOT_RETRIEVE_FROM_OFFLINE_CACHE`.
- Lines 5661-5877: Switches from `NS_E_*` media/network constants to monitor and graphics constants in the `0xC026****` facility, ending at `ERROR_GRAPHICS_ONLY_CONSOLE_SESSION_SUPPORTED = 0xC02625E0`.

## Important APIs, Types, And Data

There are no functions or classes in this chunk. The important API is the set of public module globals created by assignment.

Representative constant families:

- DVD and media-device errors: `NS_E_DVD_COPY_PROTECT`, `NS_E_DVD_INVALID_DISC_REGION`, `NS_E_PDA_DEVICE_FULL`, `NS_E_PDA_CANNOT_TRANSCODE`, and `NS_E_IMAPI_MEDIUM_INVALIDTYPE`.
- Windows Media Player and codec errors: `NS_E_WMP_UNSUPPORTED_FORMAT`, `NS_E_WMP_CODEC_NEEDED_WITH_4CC`, `NS_E_WMP_SERVER_UNAVAILABLE`, `NS_E_WMP_AUDIO_CODEC_NOT_INSTALLED`, and `NS_E_WMP_VIDEO_CODEC_NOT_INSTALLED`.
- WMP/WMDRM and DRM lifecycle errors: `NS_E_WMP_DRM_LICENSE_EXPIRED`, `NS_E_DRM_INVALID_LICENSE`, `NS_E_DRM_NO_RIGHTS`, `NS_E_DRM_LICENSE_UNUSABLE`, `NS_E_DRM_DEVICE_NOT_REGISTERED`, and `NS_E_DRM_CERTIFICATE_REVOKED`.
- Streaming and server errors: `NS_E_UNKNOWN_PROTOCOL`, `NS_E_SERVER_UNAVAILABLE`, `NS_E_PROXY_TIMEOUT`, `NS_E_FIREWALL`, `NS_E_MMS_NOT_SUPPORTED`, and `NS_E_PUSH_CANNOTCONNECT`.
- Metadata/query errors: `NS_E_PROPERTY_NOT_FOUND`, `NS_E_PROPERTY_READ_ONLY`, `NS_E_INVALID_QUERY_OPERATOR`, `NS_E_METADATA_NOT_AVAILABLE`, and `NS_E_METADATA_INVALID_DOCUMENT_TYPE`.
- Monitor/graphics errors: `ERROR_MONITOR_INVALID_DESCRIPTOR_CHECKSUM`, `ERROR_GRAPHICS_INVALID_DISPLAY_ADAPTER`, `ERROR_GRAPHICS_NO_VIDEO_MEMORY`, `ERROR_GRAPHICS_INVALID_VIDPN_TOPOLOGY`, `ERROR_GRAPHICS_MONITOR_NOT_CONNECTED`, `ERROR_GRAPHICS_OPM_NOT_SUPPORTED`, and `ERROR_GRAPHICS_DDCCI_INVALID_MESSAGE_CHECKSUM`.

The values are Python `int` objects. Their sign is not converted to signed 32-bit representation; HRESULTs such as `0xC00D1160` and `0xC02625E0` remain positive Python integers. Callers comparing against packed wire values or Windows APIs must use the same unsigned numeric representation or explicitly normalize signed inputs.

## Control Flow

This chunk has no runtime branching, loops, function calls, imports, or exception handling. Python executes each assignment exactly once during module import. After import, consumers read constants directly from `impacket.hresult_errors`.

The only "flow" to preserve is ordering and completeness:

1. The earlier `ERROR_MESSAGES` dictionary is created first.
2. The constants section starts after the dictionary and binds each HRESULT symbol in file order.
3. This chunk completes that constants section and reaches EOF, so no later code transforms or validates the constants.

Because the assignments are independent, changing one line affects only that one symbol unless two symbols are intentionally expected to share a value elsewhere in the file. This range does not define aliases via references to earlier names; each name is assigned a literal hex integer.

## State And Persistence Behavior

- State is import-time module state only. Each assignment adds or replaces a key in the module globals dictionary.
- There is no on-disk persistence, no cache file, no mutable collection in this chunk, and no external side effect beyond imported module globals.
- Re-import uses normal Python module caching through `sys.modules`; the assignments run once per interpreter process unless the module is reloaded.
- The constants are not frozen. Python callers could monkey-patch names on the module, so tests that require catalog integrity should import a fresh interpreter or reload the module before checking exact values.
- `ERROR_MESSAGES` is not updated by these assignments. If a constant is corrected here but the earlier dictionary is not corrected, symbolic access and lookup-message access can diverge.

## Dependencies And Integration Points

This chunk has no direct imports or library dependencies. Its dependency is semantic: the numeric values and symbolic names are intended to mirror Microsoft's `[MS-ERREF]` HRESULT definitions.

Integration points are module consumers that need named HRESULTs:

- DCERPC, COM, SMB, or Windows protocol helpers can compare numeric return codes against these globals rather than embedding raw integers.
- Error-formatting code can use `ERROR_MESSAGES` for descriptions and these constants for readable comparisons in tests or protocol branches.
- Downstream applications importing Impacket can reference constants such as `NS_E_BAD_REQUEST` or `ERROR_GRAPHICS_OPM_INVALID_HANDLE` without maintaining their own HRESULT table.

The file comment says "Ideally all the files should grab the error codes from here", which positions this module as a central catalog. This chunk is therefore data infrastructure rather than protocol logic.

## Risks And Edge Cases

- Catalog drift is the primary risk. The file appears generated or mechanically copied from `[MS-ERREF]`; manual edits can introduce wrong hex values, misspell names, or omit gaps in the official table.
- There is no runtime validation that each constant has a matching `ERROR_MESSAGES` entry. A named constant may be usable for comparisons even if lookup formatting lacks the matching message, or vice versa.
- Names are close to official Windows identifiers but include existing spelling quirks from the source table, such as `NS_E_METADATA_LANGUAGE_NOT_SUPORTED`. Correcting spelling would be a breaking API change for callers that import the current symbol.
- Some constants are very similar across families, for example WMP DRM names in the `0xC00D11xx` and `0xC00D12xx` ranges and generic DRM names in the `0xC00D27xx` to `0xC00D28xx` ranges. Tests should avoid assuming that similar names imply identical values or interchangeable semantics.
- The unsigned Python integer representation can surprise code that receives signed HRESULTs from ctypes or packed protocol fields. Comparisons should normalize to 32-bit unsigned values when needed.
- The late graphics constants include long identifiers such as `ERROR_GRAPHICS_EMPTY_ADAPTER_MONITOR_MODE_SUPPORT_INTERSECTION` and `ERROR_GRAPHICS_DDCCI_CURRENT_CURRENT_VALUE_GREATER_THAN_MAXIMUM_VALUE`; mechanical line wrapping or formatting changes could accidentally alter the identifier text.
- Because this is EOF, adding new constants after line 5877 changes the module's public surface and should be coordinated with any generated-source process rather than appended casually.

## Test Signals

- Import smoke test: `import impacket.hresult_errors as h` should succeed, proving every assignment in the constants tail is syntactically valid.
- Boundary value checks should cover the start and end of this chunk, for example `h.NS_E_DVD_DISC_COPY_PROTECT_OUTPUT_NS == 0xC00D1160` and `h.ERROR_GRAPHICS_ONLY_CONSOLE_SESSION_SUPPORTED == 0xC02625E0`.
- Family checks should sample each major range: WMP, PDA/sync, cURL/content partner, namespace/cache/publishing point, encoder/source-group, DRM, streaming/network, metadata, monitor, and graphics.
- Cross-surface checks should compare selected constants against `ERROR_MESSAGES` keys and names when entries exist, such as verifying the same integer key resolves to the same symbol string in the earlier dictionary.
- Unsigned-normalization tests should assert that HRESULT values above `0x80000000` compare equal after masking signed inputs with `0xffffffff`.
- Static catalog tests can parse the assignment section and flag duplicate names, non-hex literals, missing `NS_E_*` or `ERROR_GRAPHICS_*` families, and values that do not match the authoritative `[MS-ERREF]` source used by the project.
