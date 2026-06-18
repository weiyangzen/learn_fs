# File Research: sources/local-fs/xfsprogs/repair/protos.h

## Role

`protos.h` is a central declaration header for major xfs_repair phase entry points and shared setup/superblock helpers.

## Interface

It declares initialization, superblock verification/read/write helpers, geometry extraction, AG buffer allocation, inode list printing, error string formatting, thread initialization, phase functions `phase1` through `phase7`, realtime metadata checking, and `verify_set_agheader()`.

## Dependencies

The declarations reference libxfs initialization, XFS mount/superblock/AG buffer types, and repair phase implementation files.

## Risk Areas

This header is broad and shared; signature drift between phase files and this header would break repair orchestration.
