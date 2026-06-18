# sources/user-network-fs/samba/source4/torture/raw/ioctl.c

Purpose: This file tests selected SMB1 raw IOCTL and NTIOCTL/FSCTL behaviors, including unsupported requests, invalid handles, sparse-file marking, and batch oplock request behavior.

Important APIs, types, and functions: `test_ioctl()` uses `RAW_IOCTL_IOCTL` with request `0xffff`, `IOCTL_QUERY_JOB_INFO`, and a bad handle. `test_fsctl()` uses `RAW_IOCTL_NTIOCTL` for `FSCTL_FIND_FILES_BY_SID`, `FSCTL_SET_SPARSE`, and `FSCTL_REQUEST_BATCH_OPLOCK`. `torture_raw_ioctl()` sets up and tears down `\\rawioctl`.

Control flow: The suite creates `test.dat`, checks legacy IOCTL requests return DOS server error, and verifies a deliberately bad handle also returns the same legacy error. For FSCTLs, it passes random non-SID data to `FSCTL_FIND_FILES_BY_SID` and accepts invalid-parameter, not-implemented, or not-supported. It then marks the file sparse and requires success. It attempts a batch oplock upgrade and logs whether the server supports it. Finally it changes the fnum to a bad handle and requires `NT_STATUS_INVALID_HANDLE`.

State and persistence behavior: It creates and removes `\\rawioctl\\test.dat`. `FSCTL_SET_SPARSE` mutates file metadata before the directory is deleted. `SMBexit` is called before tree deletion.

Dependencies and integration points: The file depends on SMB raw IOCTL wrappers, SMB constants, FSCTL codes, random buffer generation, `create_complex_file()`, and directory setup/deletion helpers.

Risks: Some FSCTL results are intentionally tolerant, but sparse-file support is required by this test. Legacy IOCTL error mapping differs from NTIOCTL error mapping, so changing server error translation can break assertions.

Test signals: Passing shows unsupported IOCTL paths, invalid handle detection, sparse marking, optional batch oplock reporting, and FSCTL invalid-input behavior conform to expected SMB1 raw client semantics.
