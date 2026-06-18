# Research: sources/user-network-fs/samba/source4/torture/vfs/fruit.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-010009`: lines 1-7330, `Docs/researches/chunks/subset-b-010009_research.md`
- `subset-b-010010`: lines 7331-8891, `Docs/researches/chunks/subset-b-010010_research.md`

## Chunk Research

### subset-b-010009: lines 1-7330

# sources/user-network-fs/samba/source4/torture/vfs/fruit.c lines 1-7330

## Chunk Scope

This chunk covers the first 7,330 lines of Samba's `source4/torture/vfs/fruit.c`. It starts at the file header and includes most of the SMB2 torture tests for `vfs_fruit`: AFP metadata packing, resource fork stream behavior, AppleDouble conversion fixtures, AAPL create-context negotiation, stream enumeration, copyfile/copychunk behavior, NFS ACE handling, and the empty-stream matrix. The range ends inside the `osx_adouble_dir_w_xattr` AppleDouble fixture; the tests that consume that directory fixture are outside this chunk.

Large static byte arrays are present in this range. They are not executable control flow, but they are important test fixtures: `metadata_xattr`, `osx_adouble_w_xattr`, `osx_adouble_without_xattr`, `osx_adouble_non_empty_rfork_w_xattr`, and the beginning of `osx_adouble_dir_w_xattr`. The comments decode their AppleDouble or Netatalk metadata structure and document expected FinderInfo, resource fork, and extended-attribute payloads.

## Purpose

`fruit.c` is a Samba torture test file for the `vfs_fruit` module and related SMB2/Mac interoperability behavior. The tests exercise how Samba exposes Apple metadata and resource forks through SMB named streams, Apple AAPL SMB2 extensions, AppleDouble conversion, Netatalk extended attributes, stream lifecycle rules, and macOS-compatible quirks.

The code is built around observable SMB2 semantics rather than internal `vfs_fruit` implementation details. It creates files/directories on a test share, writes or injects Apple metadata, negotiates AAPL extensions when needed, then asserts exact stream lists, NTSTATUS values, EOF sizes, read data, copychunk responses, ACL shapes, and directory enumeration metadata. Many tests encode macOS behavior that Samba intentionally emulates, including non-intuitive AFP_AfpInfo reads beyond the logical 60-byte size and different deletion semantics for metadata streams versus resource forks.

## Important Fixtures

- `metadata_xattr` models a Netatalk metadata extended attribute containing file dates, FinderInfo with type/creator `BARRFOOO`, and AFP file info. `test_read_netatalk_metadata` writes it directly to the local share path using `setxattr()` and then verifies Samba exposes it as `AFP_AfpInfo`.
- `osx_adouble_w_xattr` is an AppleDouble file with FinderInfo, resource fork, and embedded `ATTR` extended attributes. Its xattrs include macOS metadata and a stream name containing an illegal NTFS colon encoded through the private-use character convention.
- `osx_adouble_without_xattr` is an AppleDouble file with resource fork and FinderInfo but without embedded xattr data. It is used to verify conversion still migrates FinderInfo and resource data.
- `osx_adouble_non_empty_rfork_w_xattr` is like the xattr fixture but with the resource fork payload intentionally made non-empty in the checked area. `test_adouble_conversion` expects bytes `0xf0` through `0xff` at offset 16 of `AFP_AfpResource`.
- `osx_adouble_dir_w_xattr` begins at the end of this chunk. The decoded comment shows an AppleDouble record for a directory with FinderInfo, a quarantine xattr, and a resource fork entry. Its consumer tests continue after line 7330.

## Important APIs, Types, And Helpers

- `BASEDIR`, `FNAME_CC_SRC`, and `FNAME_CC_DST` define shared test names. Most tests create all state under `vfs_fruit_dir` and clean it with `smb2_deltree()`.
- `CHECK_STATUS` and `CHECK_VALUE` are local assertion macros that report a torture failure and jump to `done`.
- `AFPINFO_EA_NETATALK` and `AFPRESOURCE_EA_NETATALK` select the platform-specific xattr names used by Netatalk interop tests. FreeBSD/`attropen` platforms use unprefixed names; Linux-style platforms use `user.org.netatalk.*`.
- `AfpInfo` comes from `MacExtensions.h`. `torture_afpinfo_new()` initializes signature, version, and backup time. `torture_afpinfo_pack()` serializes the 60-byte AFP info blob with `RSIVAL()` and copies FinderInfo at offset 16.
- `torture_write_afpinfo()` opens `<file>:AFP_AfpInfo` with `NTCREATEX_DISP_OVERWRITE_IF` and writes the packed 60-byte blob.
- `check_stream()` opens a named stream, reads an exact byte count at an offset, and compares a selected subrange. If the expected value is `NULL`, missing streams are considered success.
- `read_stream()` returns the number of bytes read from a stream and treats `NT_STATUS_END_OF_FILE` as a non-fatal condition for EOF boundary tests.
- `write_stream()` opens a file or stream with `NTCREATEX_DISP_OPEN_IF` and writes data at an offset.
- `torture_setup_local_xattr()` bridges SMB-level tests with local filesystem state by using the configured `localdir`/share path and `setxattr()`.
- `torture_setup_file()` creates either a file or directory over SMB2 with broad share access and normalizes cleanup before creation.
- `enable_aapl()` sends an SMB2 CREATE on the root path with the `AAPL` create context and verifies returned server capabilities. This call intentionally changes AAPL behavior for the SMB session.
- `check_stream_list()` and `check_stream_list_handle()` query `RAW_FILEINFO_STREAM_INFORMATION`, sort both expected and actual stream names, and compare exact stream sets.
- The copy helpers (`write_pattern`, `check_pattern`, `test_setup_copy_chunk`, `check_copy_chunk_rsp`, `copy_one_stream`, `copy_finderinfo_stream`) construct SMB2 FSCTL copychunk requests and validate file/stream copy results.
- `check_nfs_sd()` validates that a security descriptor has exactly one NFS mode, one NFS uid, and one NFS gid ACE domain entry.
- `struct tcase`, `struct tcase_results`, and `subtcase_t` drive the empty-stream matrix. They encode expected size, open status, and stream visibility before and after closing handles for AFPInfo, AFPResource, and ordinary streams.

## Control Flow And Test Coverage

The test functions generally follow a common pattern:

1. Allocate a temporary talloc context.
2. Remove any prior `BASEDIR` tree or test file.
3. Create a base directory and file.
4. Optionally negotiate AAPL extensions or inject local xattrs/AppleDouble files.
5. Open, write, truncate, delete, copy, enumerate, or query SMB2 streams.
6. Assert exact NTSTATUS values, stream lists, file sizes, and data bytes.
7. Close handles and clean the test tree.

The first group validates AFP metadata and resource forks:

- `test_read_netatalk_metadata()` requires a configured `localdir`, writes the Netatalk metadata xattr locally, and verifies `AFP_AfpInfo` reads expose the AFP signature and FinderInfo. It also checks odd EOF behavior for reads at offsets 59, 60, and 61.
- `test_read_afpinfo()` creates an AFPInfo stream through SMB and verifies the same read-boundary behavior, including the macOS-compatible behavior where reads with offsets up to 60 return data as if from offset 0.
- `test_write_atalk_metadata()` writes FinderInfo type/creator data and reads it back from `AFP_AfpInfo`.
- `test_write_atalk_rfork_io()` writes `AFP_AfpResource` at sparse offsets, checks resulting resource fork sizes, and truncates the resource fork to one byte.
- `test_rfork_truncate()` verifies that truncating an open resource fork to zero removes visibility for new opens while preserving valid behavior for existing and newly recreated handles.
- `test_rfork_create()` verifies that creating an empty resource fork does not make it visible as a real stream until it has data.
- `test_rfork_fsync()` covers the regression noted for bug 15182: creating, writing, and flushing a resource fork must succeed.
- `test_rfork_create_ro()` confirms that `OPEN_IF` with read-only access can create/open a resource fork without requiring write access.

The AppleDouble conversion tests then use the embedded fixture arrays:

- `test_adouble_conversion()` writes `._test_adouble_conversion` using `osx_adouble_non_empty_rfork_w_xattr`, then reads the base file's `AFP_AfpResource`, `AFP_AfpInfo`, xattr-derived stream, and expected stream list. This is Samba-only and skips on an OS X server.
- `test_adouble_conversion_wo_xattr()` uses `osx_adouble_without_xattr`, negotiates AAPL, triggers server-side conversion via `smb2_find_level()`, and verifies only default, AFPInfo, and AFPResource streams exist.

The AAPL and directory enumeration block tests session-level Apple extension behavior:

- `test_aapl()` sends an `AAPL` create context requesting server caps, volume caps, and model info. It validates command, reply bitmap, server capability bits, model string conversion from UTF-16LE, and AAPL-enriched `SMB2_FIND_ID_BOTH_DIRECTORY_INFO` results. After writing FinderInfo and a 3-byte resource fork, it expects the resource fork length in `short_name_buf[0..7]` and FinderInfo at `short_name_buf + 8`.
- `test_readdir_attr_illegal_ntfs()` creates a file whose visible name includes the private-use replacement for an illegal NTFS colon, writes metadata/resource fork data, and checks AAPL directory enumeration preserves the encoded name while returning macOS metadata.
- `test_stream_names()` creates a stream whose name encodes an illegal colon and verifies stream enumeration returns the normalized `:foo<private-use>bar:$DATA` plus the default stream.

The copy tests exercise SMB server-side copy semantics:

- `test_copyfile()` first verifies a zero-chunk `FSCTL_SRV_COPYCHUNK` without AAPL copyfile support returns success with zero total bytes copied. It then negotiates AAPL `SUPPORTS_OSX_COPYFILE`, creates a source file with default data, an AFP resource fork, and an additional named stream, issues zero-chunk copyfile semantics, and verifies main file data plus both streams were copied.
- `test_copy_chunk_streams()` verifies ordinary named streams, `AFP_AfpResource`, and `AFP_AfpInfo` can be copied with one explicit copychunk descriptor.

The deletion/truncation tests focus on lifecycle differences:

- `test_afpinfo_enoent()` verifies that opening missing `AFP_AfpInfo` with stat-style access returns `NT_STATUS_OBJECT_NAME_NOT_FOUND`.
- `test_create_delete_on_close()` and `test_setinfo_delete_on_close()` show `AFP_AfpInfo` can be deleted by create delete-on-close or setinfo delete-on-close. While a delete-on-close handle is open, new opens see `NT_STATUS_DELETE_PENDING`; after close, stream enumeration drops back to default only.
- `test_setinfo_eof()` confirms `AFP_AfpInfo` cannot be extended past 60 bytes, and truncation to 1 or 0 succeeds but does not remove or alter the FinderInfo stream.
- `test_afpinfo_all0()` writes a valid AFPInfo blob with zero FinderInfo and confirms stream enumeration suppresses the AFPInfo stream even while the stream handle remains usable for metadata updates.
- `test_create_delete_on_close_resource()` and `test_setinfo_delete_on_close_resource()` show `AFP_AfpResource` differs: delete-on-close does not remove the resource stream in the same way AFPInfo does.
- `test_setinfo_eof_resource()` shows setting resource fork EOF to 1 changes its size, and setting EOF to 0 deletes the resource stream.
- `test_setinfo_stream_eof()` applies the same style of checks to an ordinary `:foo` stream, including EOF 21, EOF 0 removal, EOF 1 recreation, AAPL-enabled zero truncation, base-file truncation, and writes after EOF zeroing.

Other covered behavior:

- `test_null_afpinfo()` uses compounded SMB2 create+read to verify a newly created AFPInfo stream reads as the default 60-byte metadata blob, then writes and validates FinderInfo.
- `test_delete_file_with_rfork()` verifies deleting a base file also removes its resource fork backing state.
- `test_rename_and_read_rsrc()` verifies a base file rename fails while a resource fork is open, with expected status differing between macOS and Samba, and that writes through the open resource fork handle still work.
- `test_invalid_afpinfo()` uses a second non-fruit share to create an invalid AFPInfo stream. The fruit share must hide the bad stream and fail opens with `OBJECT_NAME_NOT_FOUND`.
- `test_writing_afpinfo()` runs a large offset/size matrix for writes to `AFP_AfpInfo`. It expects all-zero writes to be invalid, accepts only writes large enough to contain a valid AFPInfo header/signature according to offset/size, and checks stream visibility/FinderInfo results. It has an option for the macOS Radar 45759458 behavior via `broken_osx_45759458`.
- `test_zero_file_id()` verifies `create.out.on_disk_id` is non-zero normally but all zero after AAPL is negotiated when the share is configured for `fruit:zero_file_id=yes`.
- `test_nfs_aces()` negotiates AAPL, gets a security descriptor, adds duplicate NFS uid/gid ACEs, writes it back, and verifies Samba condenses the NFS mode/uid/gid domain entries back to exactly one each.
- `test_empty_stream()` opens a second SMB2 connection and runs the table-driven empty-stream matrix across AFPInfo read-only, AFPInfo read/write, AFPResource read-only, AFPResource read/write, ordinary stream read-only, and ordinary stream read/write cases. Each case checks size, open status from same and different clients, stream visibility while handles are open, final status after close, EOF-zero behavior, overwrite behavior, and delete-on-close behavior.

## State And Persistence Behavior

The tests manipulate three kinds of persistent state:

- SMB files and named streams on the test share, mostly under `vfs_fruit_dir`.
- Local filesystem extended attributes when a test needs Netatalk interop or AppleDouble conversion seed data.
- Session-level AAPL extension state, which is enabled by a special SMB2 CREATE context and then affects later operations in the same SMB session.

`AFP_AfpInfo` is treated as a logical 60-byte metadata stream. Its serialized form includes signature, version, backup time, and FinderInfo. Several tests assert that this stream may be suppressed from enumeration when it contains only default or zero FinderInfo. Writes that cannot form a valid AFPInfo are rejected with `NT_STATUS_INVALID_PARAMETER`.

`AFP_AfpResource` is treated like the resource fork data stream. It may have sparse writes, real EOF changes, and deletion when EOF is set to zero. The tests intentionally distinguish it from AFPInfo, which has fixed-size logical metadata behavior.

AppleDouble conversion persists data by creating `._` files and then triggering server-side conversion through stream access or directory enumeration. After conversion, the base file should expose migrated AFPInfo, AFPResource, and xattr-derived streams; later chunks cover additional conversion/deletion cases.

The empty-stream tests are especially stateful. They verify that stream visibility can depend on whether a handle remains open, whether data has actually been written, whether EOF was set to zero, and whether a second SMB2 client sees the same state.

## Dependencies And Integration Points

Primary dependencies visible in this chunk:

- Samba torture framework: `struct torture_context`, `torture_assert_*`, `torture_skip`, suite registration helpers outside this range, and SMB2 test utilities.
- SMB2 client APIs: `smb2_create`, `smb2_create_send/recv`, `smb2_read`, `smb2_util_write`, `smb2_util_close`, `smb2_getinfo_file`, `smb2_setinfo_file`, `smb2_find_level`, `smb2_ioctl`, `smb2_lock`, `smb2_flush`, and utility helpers for unlink/rmdir/deltree/testdir/testfile.
- SMB2 create contexts: `smb2_create_blob_add()`, `smb2_create_blob_find()`, and `SMB2_CREATE_TAG_AAPL`.
- Mac extension constants and types from `MacExtensions.h`, including AFP stream names, AFP info sizes, signatures, and AAPL capability bits.
- NDR ioctl structures for `FSCTL_SRV_REQUEST_RESUME_KEY` and `FSCTL_SRV_COPYCHUNK`.
- Security descriptor APIs and Unix NFS SID domains for AAPL NFS ACE tests.
- Local xattr APIs from `system/filesys.h` for Netatalk metadata injection.
- Runtime torture settings: `localdir`, `osx`, and `broken_osx_45759458` adjust expectations or skip behavior.

The tests are integration tests for share configurations. Some require Samba with `vfs_fruit`; some require `fruit:metadata=netatalk`, `fruit:zero_file_id=yes`, AAPL support, streams/xattr behavior, a second non-fruit share, or a local path setting.

## Risks And Edge Cases

- AAPL negotiation is session-scoped. Tests that call `enable_aapl()` can change behavior for later operations on the same tree/session, so ordering and cleanup matter.
- AFPInfo semantics are intentionally surprising: fixed logical size, special read offsets, invalid short writes, stream suppression for zero/default FinderInfo, and no deletion on EOF zero. Regressions here can look like ordinary stream behavior but break macOS clients.
- AFPResource semantics are closer to ordinary data streams, but not identical. Zero-length resource forks may be hidden, and open handles must remain coherent across truncate/recreate cases.
- AppleDouble conversion relies on exact binary fixture layout. Small fixture changes can alter expected FinderInfo, resource fork bytes, xattr-derived stream names, or conversion trigger behavior.
- Stream names with illegal NTFS characters use private-use Unicode substitutions in source literals. Incorrect normalization can break stream enumeration and AAPL readdir attributes even if raw stream I/O still works.
- Copyfile semantics overload zero-chunk `FSCTL_SRV_COPYCHUNK` after AAPL copyfile negotiation. The same ioctl has different expected total bytes before and after negotiation.
- Several tests skip or change expectations on macOS servers. Samba and macOS compatibility are deliberately compared but not identical.
- The empty-stream matrix closes handles inside helper routines and also has outer cleanup. Handle lifetime bugs can mask stream visibility issues or cause false sharing/delete-pending results.
- This chunk stops at the beginning of the directory AppleDouble byte array. Any final interpretation of directory AppleDouble conversion must be reconciled with the following chunk where the fixture and consumer tests complete.

## Test Signals

Strong validation signals for this chunk include:

- `smbtorture` fruit suite cases passing for metadata read/write, resource fork I/O, resource fork truncation/create/fsync, AAPL negotiation, stream names, copyfile, copychunk streams, NFS ACEs, invalid AFPInfo, AFPInfo write matrix, stream EOF, and empty-stream behavior.
- Exact NTSTATUS checks: `OK`, `OBJECT_NAME_NOT_FOUND`, `DELETE_PENDING`, `INVALID_PARAMETER`, `ALLOTTED_SPACE_EXCEEDED`, and macOS/Samba-specific rename failures.
- Stream list checks returning only expected streams, especially default-only suppression for empty AFPInfo/resource/ordinary streams and exact inclusion of `AFP_AfpInfo`, `AFP_AfpResource`, and encoded illegal-colon streams after data writes or conversion.
- Byte checks for FinderInfo values such as `BARRFOOO`, `SMB,OLE!`, `TESTSLOW`, `WAVEPTul`, and `FOO BAR `.
- Resource fork size checks after sparse writes, EOF changes, copyfile, and copychunk.
- AAPL directory enumeration checks for returned capability bits, model string, resource fork length, FinderInfo in `short_name_buf`, and zero on-disk file IDs when configured.
- Cross-client checks in `test_empty_stream()` confirming same-client and different-client visibility agree with the table expectations while handles are open and after they close.
- Samba-only AppleDouble conversion tests skipping on macOS while passing on Samba with fixture-derived metadata and streams.

### subset-b-010010: lines 7331-8891

# sources/user-network-fs/samba/source4/torture/vfs/fruit.c lines 7331-8891

## Scope

This chunk covers lines 7331-8891 of `sources/user-network-fs/samba/source4/torture/vfs/fruit.c`. It is the tail of Samba's SMB2 `vfs_fruit` torture tests. The range starts in the middle of the `osx_adouble_dir_w_xattr` AppleDouble directory fixture byte array, then defines several focused tests and suite factories:

- Directory AppleDouble conversion and delete/open behavior around `test_delete_trigger_convert_sharing_violation()`.
- AAPL-negotiated locking and case-insensitive find checks.
- The main `torture_vfs_fruit()` suite registration for all general fruit tests.
- Netatalk-specific stream-name and locking-conflict tests, plus their suite.
- File-ID, Time Machine volume-size, conversion, unfruit, and AFPInfo validation suite/test entry points.

The chunk depends heavily on helpers and fixtures defined earlier in the same file, including `BASEDIR`, `AFPINFO_STREAM`, `AFPRESOURCE_STREAM_NAME`, `osx_adouble_w_xattr`, `test_zero_file_id()`, `enable_aapl()`, `write_stream()`, `check_stream()`, `check_stream_list()`, `torture_setup_file()`, `torture_write_afpinfo()`, and `torture_afpinfo_new()`. Those helpers are not redefined in this range.

## Purpose

The covered code tests Samba's `vfs_fruit` compatibility layer for macOS SMB clients and Netatalk interoperability. The behavior under test is mostly not ordinary file I/O; it is the translation between Apple metadata/resource forks, NTFS-style alternate data streams, AppleDouble sidecar files, AAPL SMB2 create contexts, sparsebundle Time Machine accounting, and Netatalk-compatible byte-range locking.

The chunk validates that:

- AppleDouble directory data can coexist with an existing non-empty `AFP_AfpInfo` stream and another named stream without causing a sharing violation during a later directory delete-style open.
- A read-only SMB2 handle can still take an exclusive byte-range lock after AAPL negotiation.
- AAPL directory search remains case-insensitive and returns the original file name for a differently cased pattern.
- Fruit stream names containing colon-mapped private-use UTF-8 bytes are exposed consistently whether created over SMB or as local xattrs.
- Netatalk emulation byte-range locks cause an expected `NT_STATUS_SHARING_VIOLATION` on a second tree open even when SMB share modes themselves would otherwise be compatible.
- Time Machine sparsebundle volume-size reporting uses configured maximum size, parsed `Info.plist` band size, and current band count to synthesize `RAW_QFS_SIZE_INFORMATION`.
- AppleDouble conversion migrates Finder info and extended attributes into SMB streams, drops an empty resource fork, and optionally deletes now-empty AppleDouble sidecar files.
- The `net vfs stream2adouble` unfruit path can convert SMB streams back into an exact AppleDouble sidecar payload.
- AFPInfo validation rejects or tolerates an invalid write depending on torture settings, and leaves the AFPInfo header normalized to the expected signature and version.

## Important APIs, Types, And Functions

The static fixture `osx_adouble_dir_w_xattr` is an AppleDouble v2 encoded directory sidecar. The included comment before the chunk describes two entries: Finder info/extended attributes and a resource fork containing a mostly blank resource payload. The byte array includes an `ATTR` extended-attribute section for `com.apple.quarantine` and a resource fork payload. In this chunk it is written to `BASEDIR\\._dir` to trigger server-side directory AppleDouble conversion paths.

`test_delete_trigger_convert_sharing_violation()` builds a directory scenario with three metadata sources: a real directory, an AppleDouble sidecar for that directory, and explicit SMB streams on the directory. It writes non-zero Finder info using `AfpInfo`, rewrites the sidecar fixture, adds a second named stream, and finally opens the directory with `SEC_STD_DELETE`. The test passes if this open and close complete without surfacing a sharing violation from conversion-triggered internal opens.

`test_readonly_exclusive_lock()` negotiates AAPL extensions with `enable_aapl()`, creates a normal file, writes data, reopens it read-only with `SEC_FILE_READ_DATA | SEC_FILE_READ_ATTRIBUTE`, and sends an SMB2 lock request with `SMB2_LOCK_FLAG_EXCLUSIVE | SMB2_LOCK_FLAG_FAIL_IMMEDIATELY`. The expected status is `NT_STATUS_OK`, proving lock rights are not incorrectly tied to data-write access in this fruit/AAPL path.

`test_case_insensitive_find()` creates `BASEDIR\\TestFile.txt`, then searches the open directory handle using pattern `TESTFILE.TXT` at `SMB2_FIND_ID_BOTH_DIRECTORY_INFO` level. It expects exactly one result and verifies the returned `id_both_directory_info.name.s` is the original mixed-case name.

`torture_vfs_fruit()` is the general suite factory. It creates the `fruit` suite and registers all one-tree and two-tree tests for copyfile, metadata, resource forks, AAPL create contexts, stream names, AFPInfo edge cases, copy-chunk streams, AppleDouble conversion, NFS ACEs, empty streams, writing AFPInfo, delete-triggered conversion, read-only exclusive locks, and case-insensitive find.

`test_stream_names_local()` requires `torture:localdir`. It creates one SMB stream whose logical name contains a colon mapped to UTF-8 private-use bytes (`0xef 0x80 0xa2`), creates a second stream by directly setting a local `user.DosStream.bar:baz:$DATA` xattr, and checks the SMB stream list contains both mapped stream names plus the default data stream.

`test_fruit_locking_conflict()` uses two SMB2 trees. On the first tree it creates and opens `locking_conflict.txt`, then applies two exclusive byte-range locks: one at `0x7ffffffffffffffc` for the Netatalk resource-fork deny-write marker area, and one from offset 0 through `0x7ffffffffffffff7`. It then attempts to open the file for read/write on the second tree and expects `NT_STATUS_SHARING_VIOLATION`.

`torture_vfs_fruit_netatalk()` registers Netatalk-oriented tests that require `fruit:metadata=netatalk`: reading Netatalk metadata, local-xattr stream names, and the two-tree locking conflict.

`torture_vfs_fruit_file_id()` registers `test_zero_file_id()` under a suite requiring `fruit:zero_file_id=yes`. The implementation of `test_zero_file_id()` is earlier in the file; this chunk only exposes it as the `fruit_file_id` suite.

`test_timemachine_volsize()` creates `test.sparsebundle`, writes a minimal `Info.plist` with `band-size` set to `8192`, creates a `bands` directory, obtains a root handle, and calls `smb2_getinfo_fs()` for `RAW_QFS_SIZE_INFORMATION`. It first checks that zero bands do not crash the server, then creates two band files and asserts the synthesized geometry: `sectors_per_unit == 2`, `bytes_per_sector == 512`, `total_alloc_units == 32`, and `avail_alloc_units == 16`.

`test_convert_xattr_and_empty_rfork_then_delete()` is a two-share conversion test. It creates a normal file and an AppleDouble sidecar containing xattrs and an empty resource fork, negotiates AAPL on the fruit-enabled tree, runs a directory `smb2_find_level()` to trigger server-side conversion, and then checks that four streams exist: default data, AFPInfo, a `com.apple.metadata:_kMDItemUserTags` stream with colon mapping, and `foo:bar` with colon mapping. It also asserts that opening the AFP resource fork returns `NT_STATUS_OBJECT_NAME_NOT_FOUND`, proving the empty resource fork was removed.

`unconvert_adfile_data` is the exact expected AppleDouble v2 output for the unfruit path. It encodes a resource fork with `bar\0`, Finder info beginning with `FOO BAR `, and an embedded `ATTR` section containing one attribute named `org.samba:woohoo` with value `bar\0`.

`test_unconvert()` creates a file with AFPInfo Finder info, a named stream whose colon is represented by private-use UTF-8, and an AFP resource stream. It then runs an external command built from torture settings: `<net> --recursive vfs stream2adouble <sharename> <BASEDIR>/`. The test opens `BASEDIR\\._unconvert` through a second share without fruit, verifies its size equals `sizeof(unconvert_adfile_data)`, and compares the entire sidecar file byte-for-byte with `check_stream()`.

`test_fruit_validate_afpinfo()` creates a file, writes valid AFPInfo first, then opens the AFPInfo stream directly and attempts to write a 60-byte buffer with payload at offset 16 but without a valid header at offset 0. The `validate_afpinfo` torture setting controls whether `NT_STATUS_INVALID_PARAMETER` is expected. After the write attempt, the test checks that the first 8 bytes of the AFPInfo stream are normalized to `AFP_Signature` and `AFP_Version` using `PUSH_BE_U32()`.

## Control Flow

Most tests follow the same torture pattern: clear stale state with `smb2_deltree()` or `smb2_util_unlink()`, create a deterministic fixture under `BASEDIR`, perform one SMB2 operation that exercises fruit behavior, assert exact `NTSTATUS` and data results, then remove the test tree in a `done:` block.

`test_delete_trigger_convert_sharing_violation()` is deliberately ordered to stress conversion side effects. It creates both a real directory and an AppleDouble sidecar, writes AppleDouble data, writes AFPInfo directly to the directory, rewrites the sidecar, adds another named stream, and only then opens the directory for delete access. This sequence checks that fruit's on-demand sidecar conversion does not conflict with already materialized streams on the same directory.

`test_stream_names_local()` combines remote SMB and local filesystem setup. The SMB-created stream name is built from `fname` plus the first expected mapped stream name. The locally created xattr uses raw colon syntax in `user.DosStream.bar:baz:$DATA`, and `check_stream_list()` confirms the server presents the local xattr with the same private-use colon mapping conventions as the SMB-created stream.

`test_fruit_locking_conflict()` is stateful across two connections. The first open and locks establish the Netatalk conflict model; the second open happens on `tree2` specifically to verify inter-client conflict behavior rather than self-open behavior on one handle. It returns `false` by default and flips to `true` only after the expected sharing violation and close path complete.

`test_timemachine_volsize()` has two query phases. The first query after creating an empty `bands` directory is a crash guard. The second query after creating two bands performs precise allocation-unit assertions. Cleanup closes the root handle if it was opened and deletes the sparsebundle.

`test_convert_xattr_and_empty_rfork_then_delete()` uses a directory enumeration as the conversion trigger. The important transition is not file open or stream read; it is `smb2_find_level()` on the containing directory after AAPL has been negotiated. After that, all checks are performed through stream enumeration, failed resource-fork open, stream content reads, and a second directory enumeration for sidecar deletion policy.

`test_unconvert()` crosses out of the SMB2 torture helper layer by calling `system()`. It prepares the stream-backed file over the fruit share, runs `net vfs stream2adouble`, then validates the generated sidecar from a second non-fruit share. The cleanup line that would delete `BASEDIR` is commented out, so this test can leave its fixture behind for inspection or due to historical debugging needs.

## State And Persistence Behavior

The tests mutate share contents under fixed names. `BASEDIR` is the main scratch directory for most chunk tests, while `readonly_lock_test.txt`, `TestFile.txt`, `test.sparsebundle`, and `test_fruit_validate_afpinfo` are standalone names. Most tests clean up at exit, but failures before cleanup can leave sidecars, streams, or sparsebundle directories.

Apple metadata persists in several forms:

- AppleDouble sidecar files named `._dir`, `._test_adouble_conversion`, and `._unconvert`.
- SMB alternate data streams such as `AFP_AfpInfo`, `AFP_AfpResource`, and colon-mapped named streams.
- Local xattrs named as `user.DosStream.*` for Netatalk/streams_xattr behavior.
- Parsed sparsebundle state in `Info.plist` and `bands/*` for Time Machine size synthesis.

The conversion tests intentionally move state between those forms. `test_convert_xattr_and_empty_rfork_then_delete()` starts with AppleDouble data and expects Finder info and xattrs to appear as streams, while empty resource-fork state disappears. `test_unconvert()` does the reverse by starting with streams and expecting a deterministic AppleDouble sidecar.

Settings influence persistent outcomes. `delete_empty_adfiles` changes whether an empty AppleDouble sidecar should remain visible after conversion. `validate_afpinfo` changes whether an invalid AFPInfo write is expected to fail. `localdir`, `net`, and `sharename` are required for tests that interact with the local filesystem or external Samba tooling.

## Dependencies And Integration Points

The code integrates with Samba's torture framework through `torture_suite_create()`, `talloc_strdup()`, `torture_suite_add_1smb2_test()`, `torture_suite_add_2smb2_test()`, `torture_suite_add_2ns_smb2_test()`, `torture_assert_*`, `torture_comment()`, and `torture_skip()`.

SMB2 protocol operations are central: `smb2_create()`, `smb2_util_close()`, `smb2_util_write()`, `smb2_lock()`, `smb2_find_level()`, `smb2_getinfo_fs()`, `smb2_getinfo_file()`, `smb2_util_mkdir()`, `smb2_util_roothandle()`, `smb2_deltree()`, and `smb2_util_unlink()`. The tests use generated protocol structs such as `struct smb2_create`, `struct smb2_find`, `struct smb2_lock`, `struct smb2_lock_element`, `union smb_fsinfo`, `union smb_fileinfo`, and `union smb_search_data`.

Fruit-specific integration depends on AAPL negotiation via `enable_aapl()`, stream constants for AFPInfo/resource forks, AppleDouble parsing in the server, and Samba configuration options including `vfs objects = catia fruit streams_xattr`, `fruit:metadata=netatalk`, `fruit:zero_file_id=yes`, `fruit:time machine max size = 32K`, and `fruit:delete_empty_adfiles`.

The Netatalk path relies on byte-range lock offsets that encode Netatalk open/deny state. The local stream-name test requires a local filesystem path to the same share so `torture_setup_local_xattr()` can write xattrs outside the SMB protocol and then verify how the server projects them back as named streams.

The unfruit conversion path depends on the external Samba `net` binary and its `vfs stream2adouble` command. That makes `test_unconvert()` more environment-sensitive than pure SMB2 tests: it requires correct torture settings, a usable command path, and a second share view without fruit.

## Risks And Maintenance Notes

The chunk contains tests that are sensitive to exact server configuration. Running them without the expected fruit, catia, streams_xattr, Netatalk metadata, zero-file-id, or Time Machine settings can produce failures that reflect test-environment mismatch rather than product regression.

Several assertions depend on exact byte encodings. The AppleDouble fixtures and expected `unconvert_adfile_data` must stay synchronized with Samba's AppleDouble encoding rules, colon mapping, endianness, and xattr layout. A legitimate format change needs fixture updates and should preserve the documented semantic payload.

The `test_case_insensitive_find()` assertion compares the returned name to the original mixed-case spelling. That is correct for this test, but case-preserving behavior can vary with backend filesystem and share configuration; changes here should be checked against the intended Samba behavior and macOS client expectations.

`test_unconvert()` invokes `system(cmd)` with values from torture settings. It is a test-only path, but it still depends on shell command construction, path correctness, and local environment. The disabled cleanup at the end means this test can leave `BASEDIR` in place.

Locking tests use very high byte offsets to emulate Netatalk. Those constants are protocol-compatibility markers, not arbitrary stress offsets. Changing them risks no longer exercising the intended conflict path.

Cleanup is mostly best-effort. Some paths use `CHECK_STATUS`/`CHECK_VALUE` macros that jump to cleanup through shared state, but external command failure, assertion exits, or commented cleanup can leave files and streams behind. Concurrent test runs against the same share may interfere because names are fixed.

## Test Signals

Strong positive signals from this chunk include:

- `test_delete_trigger_convert_sharing_violation()` opens and closes the directory with delete access after sidecar and stream setup without `NT_STATUS_SHARING_VIOLATION`.
- `test_readonly_exclusive_lock()` receives `NT_STATUS_OK` for an exclusive byte-range lock on a read-only handle.
- `test_case_insensitive_find()` returns one `SMB2_FIND_ID_BOTH_DIRECTORY_INFO` result for `TESTFILE.TXT`, with the preserved name `TestFile.txt`.
- `test_stream_names_local()` reports exactly the two colon-mapped named streams plus `::$DATA`.
- `test_fruit_locking_conflict()` receives `NT_STATUS_SHARING_VIOLATION` on the second tree open after Netatalk-style locks are present.
- `test_timemachine_volsize()` reports 2 sectors per unit, 512 bytes per sector, 32 total allocation units, and 16 available allocation units after two 8 KiB bands under a 32 KiB max-size configuration.
- `test_convert_xattr_and_empty_rfork_then_delete()` sees four expected streams, cannot open the empty resource fork, reads `TESTSLOW` from AFPInfo at the expected offset, reads `baz` from the colon-mapped `foo:bar` stream, and sees the expected directory entry count based on `delete_empty_adfiles`.
- `test_unconvert()` produces an AppleDouble sidecar with exactly `sizeof(unconvert_adfile_data)` bytes and byte-for-byte matching content.
- `test_fruit_validate_afpinfo()` either rejects invalid AFPInfo writes with `NT_STATUS_INVALID_PARAMETER` or accepts them when configured, and in both cases verifies the first 8 bytes are the canonical AFP signature/version.

Useful regression indicators are unexpected stream-list ordering or counts, failure to map private-use colon bytes consistently, a resource fork still visible after empty-rfork conversion, Time Machine allocation values off by one band or allocation unit, failure to surface Netatalk lock conflicts, and AFPInfo headers left invalid after a failed write.

## Chunk Boundary Notes

The range begins mid-array at line 7331, so the complete AppleDouble directory fixture commentary starts before this chunk. The chunk ends with the full `test_fruit_validate_afpinfo()` function but does not show where, if anywhere, that public test symbol is registered by another suite. Whole-file reports should merge this chunk with earlier `fruit.c` chunks before making complete claims about helper definitions, all fixture origins, or complete suite exposure.
