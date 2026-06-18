# sources/user-network-fs/impacket/tests/SMB_RPC/test_ndr.py

## Purpose

`test_ndr.py` is a local golden-packet regression suite for Impacket's DCE/RPC NDR and NDR64 marshalling layer. It feeds captured or hand-built byte streams into generated RPC structures, serializes them back with `getData()`, and checks byte equality or packed length preservation for complex structures whose alignment and referent handling are easy to regress.

## Important APIs, Types, and Functions

The single test class is `NDRTests(unittest.TestCase)`. It defines `NDR64Syntax` with `uuidtup_to_bin(('71710533-BEBA-4937-8319-B5DBEF9CCC36', '1.0'))` and uses that transfer syntax where NDR64 packing matters.

The suite exercises DRSUAPI responses (`DRSCrackNamesResponse`, `DRSDomainControllerInfoResponse`, `DRSGetNCChangesResponse`), SAMR calls (`SamrLookupNamesInDomainResponse`, `SamrLookupIdsInDomain`), LSAT responses (`LsarGetUserNameResponse`, `LsarLookupSids2Response`), RRP registry calls (`BaseRegEnumValueResponse`, `BaseRegGetKeySecurityResponse`, `BaseRegQueryMultipleValues`, `BaseRegQueryValueResponse`, `RVALENT`, `REG_SZ`), SCMR (`RCreateServiceWResponse`), DCOM runtime (`ComplexPing`), SRVS (`NetrShareEnum`), and endpoint mapper types (`ept_lookupResponse`, `ept_map`, `EPMTower`, floor structures). Utility dependencies include `NULL`, `dtypes.ULONG`, `string_to_bin`, and diagnostic `hexdump`.

## Control Flow

Most tests follow the same parse-roundtrip pattern: assign a captured byte literal, instantiate the corresponding RPC object, call `fromString()`, optionally dump the decoded structure, call `getData()`, and assert exact equality or identical length. Exact equality is used where padding and all output bytes are expected to be stable; length equality is used for cases where semantically equivalent repacking may differ in filler bytes or generated referents.

Several tests construct requests from fields rather than only parsing captures. `test_10` builds `srvs.NetrShareEnum` under NDR64 with null server and resume handles. `test_12` builds an endpoint mapper tower from interface, data representation, protocol, port, and IPv4 host floors and stores the tower in `epm.ept_map(isNDR64=True)`. `test_14` creates a `SamrLookupIdsInDomain` request with a domain handle, count, two `ULONG` relative IDs, and an explicit conformant-array maximum count. `test_15` prepares three `RVALENT` registry value descriptors and a value buffer before switching a `BaseRegQueryMultipleValues` request to NDR64 and parsing a captured request.

## State and Persistence Behavior

The file has no persistent external state. State is local to each test's RPC object and nested NDR field containers. The main mutable behavior under test is `fromString()` populating nested fields, `changeTransferSyntax()` switching NDR64 layout rules, and list-like NDR arrays receiving appended entries. The tests print and dump large packets to stdout, which can produce noisy logs but does not affect assertions.

## Dependencies and Integration Points

This test module integrates many generated `impacket.dcerpc.v5` endpoint modules with the shared NDR engine. It is a broad integration signal for conformant varying strings, pointers, arrays, unions, tower floors, security descriptors, SIDs, handles, and NDR64 alignment. It also touches UUID conversion and low-level data-type wrappers that are shared by remote DCERPC clients.

## Risks and Edge Cases

The embedded byte literals are large captures, so maintenance is difficult and failures can be noisy. Some assertions compare only lengths, which can miss byte-level regressions in padding or referent values. The suite relies on captured Windows-like payloads with magic filler bytes, wide strings, SIDs, endpoint towers, OIDs, and registry value lists; a seemingly unrelated change in NDR packing can break many tests at once. There is also a likely typo in `test_15` where `item1['ve_valueptr']` is assigned twice instead of setting `item2['ve_valueptr']`; the later `fromString()` call means the constructed request fields mainly document intent rather than drive final assertions.

## Test Signals

Strong signals are exact round trips for DRSUAPI, SAMR, LSAT, RRP, SCMR, DCOMRT, and endpoint mapper responses. Length-only signals catch gross NDR64 and tower-size regressions but should be supplemented by byte equality where the marshaller is expected to be deterministic. Running this file is useful after changes to `impacket.dcerpc.v5.ndr`, NDR64 transfer syntax handling, conformant arrays, pointer referents, and endpoint mapper tower serialization.
