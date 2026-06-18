# sources/object-store/daos/src/vos/storage_estimator/common/dfs_sb.py

## Purpose
Discovers DFS superblock and VOS structure metadata from installed DAOS shared libraries and converts it into storage-estimator YAML or `vos_structures` objects.

## Important APIs, Types, And Functions
Helper functions render or parse DFS dkeys/akeys (`_print_akey`, `_print_dkey`, `_print_dfs_inode`, `_create_akey`, `_parse_dfs_sb_dkey`, `_parse_dfs_akey_inode`). `STR_BUFFER` models C string ownership. `BASE_CLASS` loads shared libraries. `VOS_SIZE` calls `get_vos_structure_sizes_yaml`; `DFS_SB` calls `dfs_get_sb_layout` and frees it through `FREE_DFS_SB`. Public helpers include `print_daos_version`, `get_dfs_sb_obj`, `get_dfs_inode_akey`, `get_dfs_sb`, and `get_dfs_example`.

## Control Flow
`DFS_SB` lazily calls the C library on first getter, then caches readiness. YAML-generation functions format returned C IOV/IOD data into estimator configuration fragments. Object-generation functions convert the same data into `DKey`, `AKey`, `VosValue`, and `VosObject` instances. `get_dfs_example` concatenates a static header, live superblock YAML, and sample file/dir template.

## State And Persistence
State is in Python wrapper objects and C-allocated memory freed in destructors. No files are written here, except callers may persist returned YAML.

## Dependencies And Integration
Depends on `ctypes`, `pydaos.raw.daos_cref`, `libdfs.so`, `daos_srv/libvos_size.so`, DAOS `VERSION`, and `storage_estimator.vos_structures`.

## Risks
Library paths are relative to this source file and require a built/installed DAOS tree. Destructor-based freeing may be fragile during interpreter shutdown. `iod_type` handling assumes values 1 and 2. YAML is assembled with string formatting rather than a YAML emitter, so unusual key bytes could break output.

## Test Signals
Tests mock comparable superblock objects in `storage_estimator_test.py`; shell smoke tests call `create_example`. Full coverage requires an environment with DAOS shared libraries.
