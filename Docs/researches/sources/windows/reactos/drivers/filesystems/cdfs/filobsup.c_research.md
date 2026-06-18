# File Research: sources/windows/reactos/drivers/filesystems/cdfs/filobsup.c

## Purpose

`filobsup.c` implements CDFS file-object context encoding and decoding. It stores the FCB in `FILE_OBJECT.FsContext` and stores the CCB plus low-bit open-type tags in `FILE_OBJECT.FsContext2`.

## Main Functions

- `CdSetFileObject`: initializes a `FILE_OBJECT` for a CDFS open type. For `UnopenedFileObject`, it clears `FsContext` and `FsContext2`. Otherwise it asserts the CCB is sufficiently aligned, stores the FCB and CCB, ORs the `TYPE_OF_OPEN` value into the low three bits of `FsContext2`, and sets `FileObject->Vpb` from `Fcb->Vcb->Vpb`.
- `CdDecodeFileObject`: extracts the open type from the low three bits of `FsContext2`. For unopened objects it returns null FCB/CCB. Otherwise it returns `FsContext` as FCB and `FsContext2` with the type bits cleared as CCB.
- `CdFastDecodeFileObject`: fast callback helper that returns the FCB and open type without returning a CCB.

## Encoding Scheme

`TYPE_OF_OPEN_MASK` is `0x7`, so only three low bits are available. `CdSetFileObject` asserts `BeyondValidType <= 8` and that the CCB pointer has those low bits clear. This relies on pointer alignment to embed the open type in the CCB pointer value.

## Dependencies

This file depends on `TYPE_OF_OPEN`, `PFCB`, `PCCB`, file-object layout, CDFS assertion macros, and ReactOS-compatible lvalue handling around `SetFlag` and `ClearFlag`.

## Research Notes

This is a small but central convention file. Every dispatch path that needs to know whether a handle is a user file, directory, volume, stream, or unopened object depends on this low-bit tagging scheme being applied consistently.
