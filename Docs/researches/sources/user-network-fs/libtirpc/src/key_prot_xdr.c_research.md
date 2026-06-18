## sources/user-network-fs/libtirpc/src/key_prot_xdr.c

Purpose: Contains rpcgen-generated XDR routines for keyserver protocol types.

Important APIs and control flow: The file encodes/decodes `keystatus`, fixed `keybuf`, netname strings, `cryptkeyarg`, `cryptkeyarg2`, discriminated `cryptkeyres`, Unix credentials, `getcredres`, `key_netstarg`, and discriminated `key_netstres`. Union result routines first serialize status and only process payload arms on `KEY_SUCCESS`.

State and persistence: No local state. In decode/free modes, dynamic memory is owned by XDR routines for strings, arrays, and netobjs.

Dependencies and integration: Used by `key_call.c`, keyserv-compatible code, and exported as part of the 0.3.2 ABI set.

Risks and test signals: Generated code assumes protocol constants such as `HEXKEYBYTES`, `MAXNETNAMELEN`, and `MAXGIDS`. Tests should round-trip each structure, verify failure arms do not touch success payloads, and exercise XDR_FREE after partial decodes.
