# sources/test-tools/pynfs/nfs4.1/server41tests/st_getdevicelist.py

Purpose: pNFS block-layout tests for device discovery, device info decoding, layout acquisition/return, and layout commit.

Important APIs/types/functions: `testGetDevList`, `testGetDevInfo`, `testGetLayout`, `testEMCGetLayout`, `testLayoutReturnFile`, `testLayoutReturnFsid`, `testLayoutReturnAll`, and `testLayoutCommit`. It uses `GETDEVICELIST`, `GETDEVICEINFO`, `LAYOUTGET`, `LAYOUTRETURN`, `LAYOUTCOMMIT`, `BlockPacker`, `BlockUnpacker`, `PNFS_BLOCK_INVALID_DATA`, `PNFS_BLOCK_READWRITE_DATA`, and `pnfs_block_layoutupdate4`.

Control flow: the tests first read `FATTR4_FS_LAYOUT_TYPES` from the export root, loop over advertised layout types, call device-list/info operations, and decode block layout device addresses. Layout tests create or open files, request block-volume layouts sized from `get_blocksize`, decode opaque extents, return layouts at file/fsid/all scopes, or mutate the final extent state and commit it with `LAYOUTCOMMIT`.

State and persistence behavior: file creation and layout commits alter server-side file and block extent state. `testLayoutCommit` specifically transitions a final extent from invalid data to read/write data and supplies a new end offset, making it the durable writeback/update path in this file.

Dependencies/integration: relies on block layout support, generated NFS types, `block` XDR helpers, `nfs4lib.state00`, and environment helpers such as `use_obj`, `create_file`, `open_file`, and `get_blocksize`.

Risks and test signals: several paths print decoded opaque structures rather than asserting deep contents. `testGetDevInfo` overrides `lo_type` to `LAYOUT4_BLOCK_VOLUME` inside a loop, which narrows coverage. `testEMCGetLayout` is a debugging test tied to a pre-existing `server2fs1/dump.eth` path. Failures mainly surface as NFS status mismatches or XDR decode failures.
