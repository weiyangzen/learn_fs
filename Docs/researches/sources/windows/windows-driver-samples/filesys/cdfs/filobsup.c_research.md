# File Research: sources/windows/windows-driver-samples/filesys/cdfs/filobsup.c

## Purpose

Provides CDFS file-object context encoding and decoding helpers.

## Main Entry Points

- `CdSetFileObject`
- `CdDecodeFileObject`
- `CdFastDecodeFileObject`

## Key Behavior

CDFS stores the FCB pointer in `FileObject->FsContext`. It stores the CCB pointer in `FileObject->FsContext2`, with the low three bits used to encode `TYPE_OF_OPEN`. `TYPE_OF_OPEN_MASK` is `0x00000007`.

`CdSetFileObject` clears both context pointers for `UnopenedFileObject`. For real opens, it asserts that the CCB pointer is quad-aligned so the low three bits are free, stores the FCB and CCB, ORs the open type into `FsContext2`, and sets `FileObject->Vpb` from the FCB's VCB.

`CdDecodeFileObject` extracts the low-bit open type from `FsContext2`. If the type is `UnopenedFileObject`, it returns null FCB/CCB. Otherwise it returns `FsContext` as the FCB and `FsContext2` with the type bits cleared as the CCB.

`CdFastDecodeFileObject` is a lighter fast-I/O helper: it asserts a valid file object, returns `FsContext` as the FCB, and returns the low-bit open type. It does not return the CCB.

## Design Notes

The code asserts that `BeyondValidType <= 8`, preserving the low-three-bit encoding contract. This file is a central dependency for dispatch, directory control, file information, FSCTL, and fast I/O paths because most request validation begins by decoding the file object's open type.
