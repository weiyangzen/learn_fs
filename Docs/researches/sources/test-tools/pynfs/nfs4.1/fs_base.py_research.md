# sources/test-tools/pynfs/nfs4.1/fs_base.py

## Purpose
`fs_base.py` defines generic extent and file-like abstractions for layout-backed files. It is a small base for sparse or externally mapped files where logical file offsets map to extents on backing volumes.

## Important APIs, Types, And Functions
- Extent type constants: `HOLE`, `VALID`, `INVALID`, and `EOF`.
- `Extent(type, v_pos, f_pos, length, volume)` records extent state, backing-volume offset, file offset, length, and volume object.
- `LayoutFile(inode, fs, size=None)` stores logical file size, current position, owning filesystem, and inode ID.
- `LayoutFile.seek`, `tell`, `read`, `write`, and `_find_extent` implement a minimal file-like API.
- `LayoutFile` expects filesystem methods `_find_extent`, `_map_extent`, and possibly `_create_hole`, though `_create_hole`/`_map_extent` are not implemented here.

## Control Flow
`seek` computes a new logical position from start/current/end and enforces bounds unless the file is resizable. `read` limits the count to bytes before EOF, repeatedly asks the filesystem for the current extent, emits zero bytes for `HOLE`, reads from the backing volume for mapped extents, advances position, and joins segments. `write` creates a hole when writing beyond EOF, maps EOF or HOLE extents before using them, writes bounded segments to the backing volume, advances position, and grows `_size`.

## State And Persistence Behavior
The object stores only logical size and current seek position. Durable data belongs to backing `volume` objects and the filesystem extent map. `size=None` makes the logical file resizable; a fixed `size` makes seek reject positions outside the current file extent.

## Dependencies And Integration Points
The file is standalone, but its classes are conceptually used by pNFS layout filesystem implementations. It requires the owning filesystem to provide extent lookup and mapping operations and backing volumes to implement `seek`, `read`, and `write`.

## Risks And Edge Cases
- `LayoutFile.write` calls `_create_hole` and `_map_extent`, but those methods are not defined in this class.
- `_find_extent` calls `self._fs._find_extent(pos, self._inode)` and raises on `INVALID`, so filesystem implementations must use the same extent contract.
- It uses text strings (`'\0'`, `"".join`) for binary file data, which is fragile under Python 3.
- `seek` does not handle unknown `whence` values and can reference `newpos` before assignment.
- Fixed-size seek requires `newpos < self._size`, rejecting a seek exactly to EOF.

## Test Signals
Tests should cover reads through holes and valid extents, writes that allocate at EOF, writes beyond EOF that create holes, invalid extent errors, non-resizable seek bounds, and filesystem/volume mock interactions for extent mapping.
