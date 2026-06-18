## sources/user-network-fs/libtirpc/src/nis.h

Purpose: Provides a minimal internal subset of NIS/NIS+ type definitions so libtirpc can compile without relying on glibc SunRPC/libnsl headers.

Important APIs and types: Defines `NIS_PK_NONE`, `nis_attr`, `nis_name`, `endpoint`, and `nis_server`. `nis_server` contains a server name, variable-length endpoint array, key type, and public key `netobj`.

State and persistence: Header-only type definitions; no runtime state.

Dependencies and integration: Supplies structures needed by AUTH_DES/NIS-related code that references NIS server metadata.

Risks and test signals: Type layout must stay compatible with expected external NIS definitions. Tests should compile consumers with and without system NIS headers, verify struct sizes/field access where ABI matters, and ensure include guards prevent duplicate definitions.
