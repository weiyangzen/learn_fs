# File Research: sources/virtualization/spdk/lib/jsonrpc/Makefile

Full-file read: 18 lines.

This Makefile builds SPDK’s `jsonrpc` library.

Main contents:
- Sets `SPDK_ROOT_DIR` and includes common SPDK make rules.
- Defines shared object version `SO_VER := 8` and `SO_MINOR := 0`.
- Builds server, server TCP, client, and client TCP sources into `LIBNAME = jsonrpc`.
- Uses `spdk_jsonrpc.map` as the symbol map.
- Includes `mk/spdk.lib.mk`.

Integration points:
- Links the JSON-RPC transport/protocol layer used by SPDK RPC servers and clients.

Risks and review notes:
- This grouped research includes client/internal files but the Makefile also builds server sources outside this work item.

Testing focus:
- Library build/link with all listed C sources.
- Symbol-map coverage after API changes.
