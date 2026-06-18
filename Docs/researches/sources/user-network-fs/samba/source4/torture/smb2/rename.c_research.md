# sources/user-network-fs/samba/source4/torture/smb2/rename.c

## Purpose
This file implements SMB2 rename torture coverage. It validates rename permission requirements, parent directory share/delete interactions, MS Word style save behavior, directory rename with open children, asynchronous directory rename stress, timestamp preservation, close full-information after rename, and renaming while another connection has the file open.

## Important APIs, Types, And Functions
`torture_smb2_rename_init()` registers the suite. Synchronous cases use `union smb_open`, `union smb_close`, `union smb_setfileinfo`, `union smb_fileinfo`, `struct smb2_create`, `struct smb2_close`, `smb2_create`, `smb2_setinfo_file`, `smb2_getinfo_file`, `smb2_close`, and `smb2_deltree`. The async benchmark uses custom tevent state machines: `rename_one_dir_cycle_send/recv()`, `rename_dir_bench_send/recv()`, and `rename_dirs_bench_send/recv()`, layered over `smb2_setinfo_file_send`, `smb2_create_send`, and `smb2_close_send`.

## Control Flow
The basic rename tests create `test_rename`, open files with different access/share masks, submit `RAW_SFILEINFO_RENAME_INFORMATION`, and assert either success or a precise failure. `simple` succeeds with delete access; `simple_nodelete` fails without delete access; `no_sharing` shows a non-shared handle can rename itself; parent-directory tests distinguish delete access and share-delete combinations that should block or allow child rename. `msword` replays observed Word 2010 access masks and create options. `rename_dir_openfile` verifies a directory cannot be renamed while it contains an open file.

The async benchmark opens or creates multiple directories in parallel, renames each directory through numbered names repeatedly, marks it delete-on-close, and closes it. `simple_modtime` creates two files separated by a five-second sleep, renames each, and confirms write timestamps are preserved. `close-full-information` creates two open handles on a source file, opens a delete-capable third handle, renames to `renamed.dat`, and verifies close responses with `SMB2_CLOSE_FLAGS_FULL_INFORMATION` still contain file attributes on both connections. `rename-open` proves a delete-capable handle can rename while a second connection has a read handle with delete sharing.

## State And Persistence
The suite creates and removes `test_rename` plus temporary files like `file.txt`, `newname.txt`, `file1.txt`, `file2.txt`, `tmp1.txt`, `request.dat`, and `renamed.dat`. Async benchmark state persists in tevent request structs until callbacks complete, and directory names mutate repeatedly. Some tests sleep for timestamp propagation or mtime differentiation.

## Dependencies And Integration Points
The file depends on SMB2 calls, tevent and `tevent_ntstatus`, torture utilities, generated security access masks, and standard sleep timing. It integrates into the SMB2 torture runner as `smb2.rename` with both one-tree and two-tree tests.

## Risks
Many access masks are raw constants or broad composed masks, so semantic changes should be checked carefully against Windows behavior. Rename behavior is sensitive to share modes, delete access, open child handles, and whether the new name already exists. The benchmark has asynchronous lifetime and cleanup risks if a callback errors before delete-on-close. Sleep-based timestamp/propagation checks can be slow or environment-sensitive.

## Test Signals
Signals include exact NTSTATUS values (`OK`, `ACCESS_DENIED`, `SHARING_VIOLATION`), successful `RAW_FILEINFO_SMB2_ALL_INFORMATION` after rename, preserved `write_time`, close full-information `file_attr == 0x20`, successful tevent polling and NTSTATUS from async benchmark, and final cleanup by `smb2_deltree()` or unlink.
