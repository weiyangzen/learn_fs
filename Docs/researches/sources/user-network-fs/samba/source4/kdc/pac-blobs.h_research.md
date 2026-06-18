## sources/user-network-fs/samba/source4/kdc/pac-blobs.h

Purpose: declarations and structures for PAC buffer list/index manipulation.

Important types and APIs: `struct type_data` stores PAC type plus optional replacement blob. `struct pac_blobs` stores type index array, ordered type blobs, and count. Public helpers create the structure from krb5 PACs, ensure required types exist, replace existing types, add blobs, and remove blobs. Macros capture type names, source location, and function name for diagnostics.

Control flow and integration: consumers use this header to validate required buffers before constructing a new PAC and to preserve or replace trusted input buffers.

State and persistence: no persistence; the structures are talloc-owned working state.

Dependencies: krb5 PAC APIs, Samba `DATA_BLOB`, generated PAC type constants, and talloc context types.

Risks: consumers must respect borrowed `DATA_BLOB` ownership. The fixed index array size must match the PAC type range constants.

Test signals: build with current generated `ndr_krb5pac.h` and unit-test macro error diagnostics for missing required buffers.
