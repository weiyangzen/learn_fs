# sources/user-network-fs/impacket/impacket/dcerpc/v5/dcom/oaut.py

## Purpose

`oaut.py` implements OLE Automation protocol data types and interface wrappers for DCOM automation. It provides NDR definitions for BSTR, VARIANT, SAFEARRAY, type information structures, `IDispatch`, `ITypeInfo`, and `ITypeComp`, plus helpers for enumerating automation methods and invoking dispatch members.

## Important APIs, Types, and Functions

Key constants are automation IIDs (`IID_IDispatch`, `IID_ITypeInfo`, `IID_ITypeComp`, `IID_NULL`) and dispatch flags such as `DISPATCH_METHOD` and `DISPATCH_PROPERTYGET`. The file defines many OAUT wire types: `DECIMAL`, `VARENUM`, `SF_TYPE`, `CALLCONV`, `FUNCKIND`, `INVOKEKIND`, `TYPEKIND`, `FLAGGED_WORD_BLOB`, `BSTR`, `CURRENCY`, `BRECORD`, SAFEARRAY variants, `VARIANT`, `DISPPARAMS`, `EXCEPINFO`, `TYPEDESC`, `FUNCDESC`, `TYPEATTR`, and related pointer/array wrappers.

RPC call classes cover `IDispatch::GetTypeInfoCount`, `GetTypeInfo`, `GetIDsOfNames`, `Invoke`, and several `ITypeInfo` methods: `GetTypeAttr`, `GetTypeComp`, `GetFuncDesc`, `GetNames`, and `GetDocumentation`. Helpers and wrappers include `enumerateMethods`, `checkNullString`, `ITypeComp`, `ITypeInfo`, and `IDispatch`.

## Control Flow

NDR structures and unions encode automation's tagged types. `FLAGGED_WORD_BLOB.__setitem__` converts Python strings into UTF-16LE code units and updates byte/character lengths; `__getitem__` decodes them back. `VARIANT` points to `wireVARIANTStr`, whose `varUnion` selects a scalar, pointer, interface pointer, SAFEARRAY, BSTR, record, null, or empty representation from the `vt` tag. Forward-reference limitations are handled by setting structures or referents dynamically in constructors such as `VARIANT_ARRAY`, `PVARIANT`, `ARRAYDESC`, and `tdUnion`.

Wrapper methods create DCOM request classes and invoke inherited `request` with the correct IID/IPID. `IDispatch.GetTypeInfo` wraps a returned interface pointer in `ITypeInfo`. `GetIDsOfNames` builds an array of null-terminated `LPOLESTR` names and returns DISPIDs. `enumerateMethods` uses type info count, type attr, function descriptions, and names to build a method/parameter map.

## State and Persistence Behavior

Module-level state is limited to constants and class definitions. Wrapper instances hold remote interface identity through `IRemUnknown2`. Local mutations occur inside NDR objects while preparing requests. There is no file persistence, but remote calls inspect or invoke automation objects and may mutate remote state depending on the target member invoked.

## Dependencies and Integration Points

The module depends on `random`, `struct`, package `LOG`, `hresult_errors`, DCOM runtime interface-pointer classes, many DCE/RPC primitive types, NDR base classes/unions/enums, and UUID conversion. It is a base dependency for DCOM modules such as `comev.py`, which import `IDispatch`, `BSTR`, and `VARIANT`.

## Risks and Edge Cases

The file is complex and contains several likely defects. `LPFUNCDESC` has duplicated `referent = (` text in the source. `IDispatch.Invoke` assigns `request['rgVarRef'] = rgVarRefIdx` instead of `rgVarRef`. `enumerateMethods` prints debug output and assumes returned structures are non-null. `checkNullString` compares strings to `NULL` and appends `'\x00'`, which can be brittle for bytes inputs. `PTYPEDESC` uses random referent IDs, affecting deterministic serialization. OAUT unions are tag-sensitive, so mismatched `vt` values can serialize invalid wire data.

## Test Signals

Tests should cover BSTR UTF-16 length/data round-trips, VARIANT encoding for scalar, BSTR, byref, null, and interface-pointer cases, SAFEARRAY union tags, `GetIDsOfNames` request construction, `Invoke` argument arrays, and type-info wrappers with mocked DCOM responses. Static/import tests should catch syntax/layout regressions in the many NDR class declarations.
