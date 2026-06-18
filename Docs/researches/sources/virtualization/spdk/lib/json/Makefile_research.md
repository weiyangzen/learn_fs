# File Research: sources/virtualization/spdk/lib/json/Makefile

Full-file read: 17 lines.

This Makefile builds SPDK’s `json` library.

Main contents:
- Sets `SPDK_ROOT_DIR` two levels up and includes `mk/spdk.common.mk`.
- Defines shared object version `SO_VER := 8` and `SO_MINOR := 0`.
- Builds `json_parse.c`, `json_util.c`, and `json_write.c` into `LIBNAME = json`.
- Uses `spdk_json.map` as the symbol map.
- Includes `mk/spdk.lib.mk`.

Integration points:
- Provides the JSON library used by JSON-RPC and many SPDK subsystems, including iSCSI RPC/config output.

Risks and review notes:
- Library ABI versioning and symbol-map updates must track exported API changes.

Testing focus:
- Build/link of `libspdk_json`.
- Symbol-map completeness for exported JSON APIs.
