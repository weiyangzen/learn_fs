# File Research: sources/local-fs/xfsdump/common/rec_hdr.h

## Role

This header defines the drive-specific tape record header used by tape-oriented drive strategies.

The structure is embedded in the drive header's `dh_specific` area for the first record and appears at the start of subsequent records.

## `rec_hdr_t`

The header records:

- magic and format version
- tape block size
- record size
- drive capability flags
- record file offset
- first mark offset within the record
- used byte count
- checksum and checksum-enabled flag
- dump UUID
- padding to match the drive-specific header region

## Semantics

The comments document that the first page of every record is reserved for the header and that the first record of a media file contains only header information, with user data beginning in the second record.
