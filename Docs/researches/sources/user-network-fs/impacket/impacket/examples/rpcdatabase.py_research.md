# sources/user-network-fs/impacket/impacket/examples/rpcdatabase.py

## Purpose
`rpcdatabase.py` provides a DCE/RPC interface UUID/version corpus for brute forcing or probing RPC endpoints. It combines a large static list of textual UUID/version pairs with Impacket's `epm.KNOWN_UUIDS`, normalizing the result into a module-level `uuid_database` set.

## Important APIs, Types, and Functions
The central data object is `uuid_database`, a `set` of UUID tuple values. It is initially built by splitting a multiline string and converting each non-empty line with `impacket.uuid.string_to_uuidtup`. The resulting UUID strings are uppercased so later matching is case-insensitive. `fix_ndr_uuid(ndruuid)` converts Impacket endpoint-mapper binary UUID keys into the tuple binary layout expected by `uuid.bin_to_uuidtup`: it asserts the input is 18 bytes, keeps the first 16 UUID bytes, unpacks the final major/minor version bytes, and appends them as little-endian unsigned shorts. The module then updates `uuid_database` with every key from `KNOWN_UUIDS`.

## Control Flow
All work happens at import time. Python evaluates the multiline UUID list, filters blank lines, converts each line into a UUID tuple, normalizes UUID text to uppercase, defines `fix_ndr_uuid`, and updates the set with converted `KNOWN_UUIDS` entries. There is no command-line entry point, class, or lazy-loading path. Callers import the module and read `uuid_database` directly.

## State and Persistence Behavior
The module is read-only after import unless a caller mutates `uuid_database` directly. It does not read or write external files and has no network side effects. The only state is the in-memory set, which deduplicates overlapping static and `KNOWN_UUIDS` entries.

## Dependencies and Integration Points
The file depends on Python `struct`, `impacket.uuid`, and `impacket.dcerpc.v5.epm.KNOWN_UUIDS`. It integrates with RPC discovery/bruteforce tooling that needs a broad list of interface UUID/version combinations to bind, query, or identify exposed DCE/RPC services.

## Risks and Edge Cases
The static database is manually embedded and may age as Windows and third-party RPC interfaces evolve. Import-time construction means malformed entries fail immediately. `fix_ndr_uuid` uses an `assert` for length validation, which can be stripped with optimized Python execution and would then produce less controlled behavior for unexpected key lengths. The temporary assignment `k = list(KNOWN_UUIDS.keys())[0]` is unused and will raise if `KNOWN_UUIDS` is empty, even though the rest of the code could otherwise tolerate an empty update.

## Test Signals
Tests should import the module, assert `uuid_database` is non-empty, verify representative static UUIDs are present in uppercase tuple form, verify all `KNOWN_UUIDS` keys convert through `fix_ndr_uuid`, and cover invalid-length input to `fix_ndr_uuid`. A regression test for duplicate handling can confirm that adding known entries does not create list-like duplicates because the database is a set.
