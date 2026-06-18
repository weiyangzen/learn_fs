# sources/user-network-fs/nfs-ganesha/src/gtest/gtest_nfs4.hh

## Purpose
This header extends the FSAL test harness with NFSv4 COMPOUND operation state and argument-building helpers. It allows unit tests to invoke individual NFSv4 operation handlers directly while still using real FSAL object handles and export context.

## Important APIs, Types, And Functions
`gtest::GaeshaNFS4BaseTest` derives from `GaneshaFSALBaseTest` and allocates `compound_data_t`, `nfs_arg_t`, one `nfs_argop4`, and one `nfs_resop4`. Helpers include `setCurrentFH`, `setSavedFH`, `set_saved_export`, `setup_lookup`, `cleanup_lookup`, `setup_putfh`, `cleanup_putfh`, `setup_rename`, `swap_rename`, `cleanup_rename`, `setup_link`, and `cleanup_link`.

## Control Flow, State, And Persistence
Setup initializes compound data, zeroes arguments/responses, creates a one-operation arg array, sets minor version zero, and defaults the single op to `NFS4_OP_PUTROOTFH` so teardown can safely free XDR structures. Teardown clears current entry, frees one compound response, frees compound data, XDR-frees `COMPOUND4args`, and then runs FSAL fixture cleanup. File-handle helpers convert FSAL handles to NFSv4 file handles with `nfs4_FSALToFhandle` and update compound current/saved entries.

## Dependencies And Integration Points
The header depends on `gtest.hh`, `nfs_file_handle.h`, `nfs_proto_functions.h`, XDR free routines, Ganesha compound state, and export reference management. It is the common support layer for NFSv4 lookup, PUTFH, RENAME, and LINK latency tests.

## Risks And Test Signals
The class name is misspelled as `GaeshaNFS4BaseTest`, so dependent tests must use that exact spelling. The single-op allocation assumes each test directly calls one handler rather than full compound dispatch. Helpers free and replace union members manually, making cleanup correctness important when tests repeatedly rebuild operation arguments.
