# Research: sources/user-network-fs/samba/source3/torture/torture.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009882`: lines 1-10421, `Docs/researches/chunks/subset-b-009882_research.md`
- `subset-b-009883`: lines 10422-16777, `Docs/researches/chunks/subset-b-009883_research.md`

## Chunk Research

### subset-b-009882: lines 1-10421

# sources/user-network-fs/samba/source3/torture/torture.c lines 1-10421

## Scope

This chunk covers the first 10,421 lines of Samba's `source3/torture/torture.c`. It starts with global torture harness setup and SMB1 client connection helpers, then covers a large collection of SMB1 behavioral tests: read/write stress, NetBench replay, tree connect/session/fid isolation, byte-range locking, oplock break/cancel paths, delete-on-close and stream delete semantics, rename/share-mode behavior, security descriptor checks, POSIX CIFS extension behavior, open attribute matrices, directory listing, IOCTL probing, chkpath, and extended attributes. The assigned range ends in the middle of `run_dirtest1()`, after the old directory listing count check and before the rest of that function's filtering validation.

## Purpose

The visible code is a standalone SMB torture test driver for exercising server behavior through Samba's SMB client APIs. Most functions are `run_*` test bodies that open one or more SMB connections, create controlled files/directories on the target share, issue protocol operations, validate NT/DOS status codes or state changes, and clean up artifacts before returning a boolean result.

The chunk focuses heavily on edge cases where an SMB server can diverge from Windows behavior:

- connection negotiation flags, signing, encryption, SPNEGO, Kerberos, SMB1 forcing, and multishare UNC selection;
- read/write integrity under repeated operations and concurrent clients;
- tree ID, user ID, process ID, and file ID isolation;
- byte-range lock stacking, timeouts, cancellation, strict lock enforcement, and POSIX/OFD lock interaction;
- oplock breaks across ordinary opens, hardlinks, ACL access, and Linux kernel leases;
- delete-on-close, stream delete, hardlink delete, print-share delete, unlink while open, and rename with/without `FILE_SHARE_DELETE`;
- DOS/NT attributes, timestamps, trans2 file info levels, `open` disposition attribute results, EAs, security descriptors, owner-rights ACEs, and SMB1 `SEC_FLAG_SYSTEM_SECURITY`;
- UNIX extension operations such as POSIX open/mkdir/unlink/hardlink/symlink/readlink/stat/chmod/getacl/setacl and case-sensitive mkdir behavior.

## Important APIs, Types, And Functions

Connection and harness helpers:

- Global configuration includes `host`, `workgroup`, `share`, `password`, `username`, `myname`, `torture_creds`, `sockops`, `torture_nprocs`, `torture_numops`, `torture_blocksize`, `use_oplocks`, `use_level_II_oplocks`, `disable_spnego`, `use_kerberos`, `force_dos_errors`, `use_multishare_conn`, `do_encrypt`, `local_path`, and `signing_state`.
- `force_cli_encryption()` verifies UNIX CIFS encryption capability and calls `cli_smb1_setup_encryption()`.
- `open_nbt_connection()` creates a NetBIOS SMB transport using `cli_connect_nb()`, applying SPNEGO/oplock/DOS-error flags.
- `smbcli_parse_unc()`, `terminate_path_at_separator()`, `torture_open_connection_share()`, `torture_open_connection_flags()`, and `torture_open_connection()` parse share names and create authenticated SMB1 share connections via `cli_full_connection_creds()`.
- `torture_init_connection()`, `torture_cli_session_setup2()`, `torture_close_connection()`, and `torture_conn_set_sockopt()` centralize session setup, secondary session creation, tree disconnect/shutdown, and socket option application.

Protocol utility wrappers:

- `cli_smbwrite()` sends legacy `SMBwrite` requests in chunks and preserves zero-byte write behavior.
- `cli_smb()` synchronously sends a raw SMB request with `cli_smb_send()`/`cli_smb_recv()` and rejects use while async calls are pending.
- `cli_bad_session_request()` writes a deliberately malformed RFC1002 session request and expects a NetBIOS negative session response with error `0x82`.
- `torture_deltree()` and `torture_delete_fn()` recursively delete a subtree through `cli_list()`, `cli_unlink()`, and `cli_rmdir()`.
- `check_error()` and `check_both_error()` validate either DOS-class/coded errors or NTSTATUS values.
- `cli_qpathinfo1()` reads `SMB_INFO_STANDARD` via `cli_qpathinfo()` and decodes DOS dates and file size/attributes.
- `cli_raw_ioctl()` sends raw `SMBioctl` requests and returns an empty `DATA_BLOB` on success.

Major test bodies visible in this chunk include `run_torture()`, `run_readwritetest()`, `run_readwritemulti()`, `run_readwritelarge()`, `run_readwritelarge_signtest()`, `run_nbench()`, `run_locktest1()` through `run_locktest13()`, `run_fdpasstest()`, `run_fdsesstest()`, `run_unlinktest()`, `run_maxfidtest()`, `run_negprot_nowait()`, `run_bad_nbt_session()`, `run_randomipc()`, `run_browsetest()`, `run_attrtest()`, `run_trans2test()`, `run_w2ktest()`, `run_oplock1()`, `run_oplock2()`, `run_oplock4()`, optional Linux `run_oplock5()`, `run_deletetest()`, `run_delete_stream()`, `run_delete_print_test()`, `run_deletetest_ln()`, `run_properties()`, `run_xcopy()`, `run_rename()`, `run_rename_access()`, `run_owner_rights()`, `run_smb1_system_security()`, `run_pipe_number()`, `run_opentest()`, `torture_setup_unix_extensions()`, `run_simple_posix_open_test()`, `run_acl_symlink_test()`, `run_posix_stream_delete()`, `run_ea_symlink_test()`, `run_posix_ofd_lock_test()`, `run_posix_blocking_lock()`, `run_posix_mkdir_test()`, `run_posix_acl_oplock_test()`, `run_posix_acl_shareroot_test()`, `run_openattrtest()`, `run_dirtest()`, `torture_ioctl_test()`, `torture_chkpath_test()`, `run_eatest()`, and the opening of `run_dirtest1()`.

Important local async state types:

- `locktest10_state`, `deferred_close_state`, `lockread_state`, `lock12_state`, and `lock_ntcancel_state` coordinate tevent-driven lock/read/close/cancel tests.
- `oplock4_state`, optional `oplock5_state`, and `posix_acl_oplock_state` coordinate oplock break waiters with competing opens or POSIX ACL fetches.
- `delete_stream_state` ensures an async base-file unlink sees `NT_STATUS_SHARING_VIOLATION` after a stream close reply ordering condition.
- `posix_blocking_state` chains POSIX lock acquisition, a blocking second lock, an echo ordering barrier, and unlock.
- `trunc_open_results` plus `open_attrs_table` and `attr_results` define expected file attribute results for truncate/open disposition combinations.

## Control Flow

Most tests follow a common control pattern:

1. Open one or more SMB connections with `torture_open_connection()`, usually forcing SMB1 and applying `sockops`.
2. Reset test files/directories with `cli_unlink()`, `cli_rmdir()`, `torture_deltree()`, `cli_setatr()`, or POSIX unlink/rmdir helpers.
3. Issue SMB operations for the scenario under test.
4. Compare status codes with explicit expected NTSTATUS/DOS errors, or compare resulting data, attributes, timestamps, sizes, ACLs, EA lists, oplock break flags, and directory counts.
5. Close fids, remove artifacts, disconnect tree/session state, and return `true` only if all checks passed.

Read/write tests use repeated deterministic or random data flows. `rw_torture()` serializes random file operations through a lock file. `rw_torture2()` writes from one connection and reads through another. `rw_torture3()` uses `procnum` to split writer/reader behavior when run under the process fan-out harness. The large-write test compares file sizes after both normal `cli_writeall()` and legacy `cli_smbwrite()`, with a variant requiring SMB signing.

Lock tests are the densest control-flow area. `run_locktest1()` checks retained locks over close and lock timeout behavior. `run_locktest2()` changes SMB PID values to verify separate lock contexts and failed unlocks from the wrong PID. `run_locktest3()` scans the 32-bit offset range. `run_locktest4()` and `run_locktest5()` test overlapping locks, recursive read locks, lock overlays, strict read/write lock enforcement, lock stack ordering, and the "NT byte range lock bug". `run_locktest6()` probes unusual `LOCKING_ANDX_CHANGE_LOCKTYPE` and `LOCKING_ANDX_CANCEL_LOCK` bits. `run_locktest7()` verifies read/write access under read and write locks from different PIDs. `run_locktest8()` reproduces a GPFS share-mode/pending-close case. `run_locktest9a()` and `run_locktest9b()` fork a local process to take a filesystem `fcntl()` lock under `local_path`, then verify the SMB lock blocks until release. `run_locktest10()` chains a short-timeout lockingX request with a read and expects the lock to conflict and the chained read to abort. `run_locktest11()` verifies lock cancel without active locks succeeds. `run_locktest12()` defers close while a chained lock/read waits on the same connection. `run_locktest13()` schedules an async blocking lock then cancels it through `tevent_req_cancel()`, requiring a quick `NT_STATUS_FILE_LOCK_CONFLICT`.

Oplock tests combine asynchronous waiters with competing operations. `run_oplock4()` first proves hardlink paths share deny-mode state, then opens one path with an oplock and asynchronously opens the hardlink path, expecting an oplock break and successful open after `cli_oplock_ack_send()`. Optional Linux `run_oplock5()` forks a child that takes a kernel lease with `F_SETLEASE`; the parent uses an SMB async open plus `cli_echo_send()` to prove the server is blocked by the kernel oplock before closing a pipe to let the child drop it. `run_posix_acl_oplock_test()` uses a Windows open with oplock and a POSIX `getacl` on a second connection to require a break.

Delete/rename/open-share tests exercise Windows-compatible lifecycle semantics. `run_deletetest()` has twelve subtests covering initial `FILE_DELETE_ON_CLOSE`, setting/unsetting delete-on-close, delete access requirements, share-delete compatibility, multiple handles and connections, read-only files, and initial delete-on-close persistence. `run_delete_stream()` intentionally races unlink of a base file against closing an alternate data stream handle and requires a sharing violation. `run_posix_stream_delete()` performs a similar stream-handle sharing check through POSIX unlink. `run_deletetest_ln()` verifies deleting one hardlink path does not remove the remaining link. `run_rename()` tests rename with different share modes and checks the renamed file gets the archive bit. `run_rename_access()` creates a destination directory with a deny ACE and confirms file and directory renames into it fail even after POSIX `chmod 0777`.

POSIX extension tests first call `torture_setup_unix_extensions()`, which verifies UNIX CIFS support and sets negotiated capabilities back on the session. `run_simple_posix_open_test()` then covers POSIX mkdir, open modes, ftruncate, stat mode/size, unlink while open, directory open errors, hardlink/symlink/readlink, POSIX lock/unlock, and interaction with a Windows-open file. `run_acl_symlink_test()` and `run_ea_symlink_test()` verify ACL and EA operations are rejected or empty on symlinks. `run_posix_ofd_lock_test()` checks POSIX locks are file-description scoped. `run_posix_blocking_lock()` uses async POSIX lock calls plus an echo barrier to show a blocking lock really waits until the original lock is released. `run_posix_mkdir_test()` checks POSIX mkdir is case-sensitive and returns `NT_STATUS_OBJECT_PATH_NOT_FOUND` for missing parent components.

The chunk ends in `run_dirtest1()`. The visible part creates `\\LISTDIR`, populates 1000 files and 1000 directories, uses `cli_list_old()` with `FILE_ATTRIBUTE_DIRECTORY`, and expects 2002 entries including `.` and `..`. The rest of the filtering and cleanup logic is in the next chunk.

## State And Persistence Behavior

The tests persist temporary server-side state on the target SMB share: files such as `\\torture.*`, lock files, `\\large.dat`, `\\delete.file`, streams like `:Zone.Identifier:$DATA`, POSIX test names, EA-bearing files, `\\LISTDIR`, and temporary names returned from `cli_ctemp()`. Most functions clean up with `cli_unlink()`, `cli_rmdir()`, `cli_posix_unlink()`, `cli_posix_rmdir()`, or `torture_deltree()` on success and failure paths, but some early returns can leave files, handles, directories, attributes, or POSIX locks behind if an intermediate operation fails.

Client-side state is mostly global or process-local:

- `current_cli`, `procnum`, `randomfname`, and `torture_nprocs` tie several tests to the external process fan-out harness.
- `use_oplocks`, `use_level_II_oplocks`, `signing_state`, `force_dos_errors`, and `do_encrypt` mutate connection behavior globally; tests that modify them usually restore saved values, but early returns can be risky.
- `local_path` is required for tests that coordinate SMB operations with local filesystem locks or kernel leases.
- `line_count` and `nbio_id` track NetBench replay progress.
- Several async tests store request completion flags in stack variables referenced by tevent callbacks, making lifetime tied to the event loop completing before function exit.
- `anonymous_shared_allocate()` in `run_oplock2()` stores child result state across `fork()`.

The code also deliberately manipulates SMB protocol identity state: `cli_state_set_uid()`, `cli_state_set_tid()`, and `cli_setpid()` are used to prove session/tree/PID isolation. Mis-restoring these fields can poison later operations on the same `cli_state`.

## Dependencies And Integration Points

This chunk depends on Samba's source3 SMB client stack and utility layers:

- SMB connection and session APIs: `cli_connect_nb()`, `cli_full_connection_creds()`, `cli_session_setup_creds()`, `cli_tree_connect_creds()`, `cli_tdis()`, `cli_shutdown()`, `smbXcli_conn_*`, and transport parsing from `lp_client_smb_transports()`.
- File protocol APIs: `cli_openx()`, `cli_ntcreate()`, `cli_close()`, `cli_writeall()`, `cli_read()`, `cli_lock32()`, `cli_locktype()`, `cli_lockingx_*`, `cli_unlink()`, `cli_rename()`, `cli_hardlink()`, `cli_getatr()`, `cli_setatr()`, `cli_qpathinfo*()`, `cli_qfileinfo*()`, `cli_list()`, `cli_list_old()`, `cli_chkpath()`, `cli_trans()`, and raw `cli_smb()`.
- POSIX/UNIX extension APIs: `SERVER_HAS_UNIX_CIFS()`, `cli_unix_extensions_version()`, `cli_set_unix_extensions_capabilities()`, `cli_posix_open()`, `cli_posix_mkdir()`, `cli_posix_stat()`, `cli_posix_unlink()`, `cli_posix_lock()`, `cli_posix_getacl()`, `cli_posix_setacl()`, `cli_chmod()`, `cli_readlink()`, and related helpers.
- Async/event APIs: `tevent_context`, `tevent_req`, `tevent_wakeup_send()`, `tevent_req_poll_ntstatus()`, `tevent_loop_once()`, async SMB create/read/close/unlink/echo/oplock helpers, and chained SMB1 request submission.
- Security APIs: `security_descriptor_dacl_create()`, `security_acl_concatenate()`, `cli_query_secdesc()`, `cli_set_secdesc()`, well-known SIDs such as `SID_WORLD`, `SID_OWNER_RIGHTS`, and `SID_NT_AUTHENTICATED_USERS`.
- Local OS integration: `fork()`, `pipe()`, `fcntl()` byte-range locks, optional Linux `F_SETLEASE`, signals, `alarm()`, `open()`, `unlink()`, and local path construction with `local_path`.
- NetBench integration: `client_oplocks.txt` and `nb_*` helpers simulate a dbench/netbench workload.
- Browser/IPC integration: `cli_NetServerEnum()` and random `\\PIPE\\LANMAN` transactions probe legacy RAP/IPC behavior.

## Risks And Maintenance Notes

- This file is a broad legacy SMB1 torture harness with many global flags. Adding tests that mutate globals must restore them on all exits or subsequent tests can run with wrong signing/oplock/SPNEGO/encryption behavior.
- Many cleanup paths use best-effort deletes and some early error returns skip cleanup or connection shutdown. Failed runs can leave share state that changes later test results.
- `run_deletetest()` contains an explicit FIXME about potential crashes if failure occurs before `cli2` initialization; its cleanup assumes partially initialized state.
- Async tests rely on strict event ordering and stack-backed callback state. If an async helper changes completion ordering or cancellation status, these tests may report failures that are timing-sensitive.
- Several tests depend on precise Windows-compatible error mapping, including distinction between DOS `ERRbadshare`/`ERRnoaccess`/`ERRbadpath` and NT status values. Protocol changes that alter status mapping can break compatibility even if the local filesystem operation succeeded.
- Tests using `local_path`, local `fcntl()` locks, or Linux kernel leases are environment-sensitive and require the SMB share to map to the supplied local path. They are not portable to all test deployments.
- Oplock and locking tests use sleeps, alarms, process forking, and timeouts. Slow or heavily loaded systems can create flaky timing signals, especially around lock timeout validation, pending close behavior, and oplock break delivery.
- Tests that open thousands of fids, pipes, files, or directories can stress server resource limits and may be unsuitable for small CI environments without isolation.
- POSIX extension tests are gated only by server capability checks; running against SMB2-only servers or SMB1 disabled environments will skip/fail these paths.
- The chunk boundary splits `run_dirtest1()`, so final per-file synthesis must merge this report with the next chunk before treating directory-list filtering behavior as fully researched.

## Test Signals

Strong signals from this chunk are explicit pass/fail returns plus printed diagnostics naming the failed operation and status. Useful regression coverage includes:

- connection helpers successfully opening encrypted, signed, SMB1-forced, oplock-capable, and multishare sessions where configured;
- read/write tests preserving data integrity across single-connection, dual-connection, multi-process, legacy `SMBwrite`, and signed large-write paths;
- lock tests returning the expected `NT_STATUS_LOCK_NOT_GRANTED`, `NT_STATUS_FILE_LOCK_CONFLICT`, `NT_STATUS_RANGE_NOT_LOCKED`, `NT_STATUS_REQUEST_ABORTED`, or timeout/cancel behavior for each scenario;
- tree/session/fid tests proving wrong TID/VUID/PID/fnum use fails rather than leaking access across contexts;
- delete and rename tests matching Windows share-delete and delete-on-close rules, including streams and hardlinks;
- POSIX extension tests validating mode/size/stat/readlink/ACL/EA/lock semantics and expected symlink denials;
- security descriptor tests enforcing deny ACEs and owner-rights ACE ordering;
- attribute/trans2/open tests returning expected timestamps, inode behavior, file attributes, open disposition outcomes, and EA counts;
- directory tests producing expected listing counts and cleanup behavior for generated trees;
- IOCTL, bad NBT session, random IPC, browser enumeration, pipe count, and maxfid tests completing without crashes or unexpected successful access.

Because this is only chunk 1 of a two-chunk oversized file, the merge lane should treat unresolved cross-chunk references as expected for `run_dirtest1()` continuation and for the final test registry/main harness that appears later in the file.

### subset-b-009883: lines 10422-16777

# sources/user-network-fs/samba/source3/torture/torture.c lines 10422-16777

## Scope

This chunk covers the tail of Samba's legacy `source3/torture/torture.c` SMB torture client. The requested range begins inside the end of `run_dirtest1()` and continues through many SMB1/SMB2/LDAP/POSIX/local utility test implementations, the `torture_ops[]` test registry, the `run_test()` dispatcher, `usage()`, and `main()`.

The file is a standalone command-line test harness for `smbtorture //server/share [options] TEST...`. The closing registry in this chunk wires tests defined earlier in the file together with tests defined in this range, so this slice is both implementation code and the main integration surface for the whole legacy binary.

## Purpose

The code in this range adds regression, stress, protocol-edge, and local-library tests to the legacy SMB torture executable. The network-facing tests exercise SMB1 and SMB2 client behavior, server error mapping, directory notifications, name mangling, POSIX extension interoperability, DFS attributes, large SMB1 reads, alternate data stream errors, session handling, and malformed SMB1 message paths. The local tests exercise Samba utility libraries without requiring a share, including substitution formatting, base64, gencache, rb-tree dbwrap, charset conversion, SID parsing/formatting, NTFS stream-name parsing, memcache, winbind client request fan-out, dbwrap transactions, tevent poll setup, hex encoding, duplicate-address removal, TDB stress loops, and path canonicalization.

The final harness code lets a user select individual tests by name or run `ALL`, applies global options such as username/password, workgroup, protocol cap, socket options, concurrency, encryption, and target filename, then returns process success or failure from the aggregate test result.

## Important APIs, Types, And Functions

Core Samba client APIs used across the network tests include `torture_open_connection()`, `torture_open_connection_flags()`, `open_nbt_connection()`, `torture_close_connection()`, `cli_ntcreate()`, `cli_openx()`, `cli_close()`, `cli_unlink()`, `cli_rmdir()`, `cli_mkdir()`, `cli_list()`, `cli_qpathinfo*()`, `cli_writeall()`, `cli_read()`, `cli_session_setup_creds()`, `cli_ulogoff()`, `cli_tree_connect()`, `smbXcli_negprot()`, `smbXcli_conn_create()`, `smb1cli_req_send()`, and `tevent_req_poll_ntstatus()`.

Important asynchronous request state types in this slice:

- `struct torture_createdel_state` and `torture_createdel_send()/recv()` create a file with `FILE_DELETE_ON_CLOSE`, then close it.
- `struct torture_createdels_state` and `torture_createdels_send()/recv()` keep a bounded pipeline of create/delete operations in flight for notification benchmarks.
- `struct swallow_notify_state` and `swallow_notify_send()` issue `cli_notify_send()` repeatedly and call a user callback for each returned `notify_change`.
- `struct pidtest_state` and `pid_echo_send()/recv()` send an SMB1 echo with an explicit 32-bit PID and validate the returned low/high PID header fields.
- `struct session_setup_nt1_truncated_state` and `smb1_session_setup_nt1_truncated_send()/recv()` manually craft a truncated SMB1 NT1 session setup request.
- `struct smb1_negotiate_exit_state` and `smb1_negotiate_exit_send()/recv()` manually send an SMB1 `SMBexit` request after negotiation.

Important network test functions defined in this range:

- `run_error_map_extract()` compares NT-status and DOS-error session setup failures by deliberately using usernames derived from NT status codes.
- `run_sesssetup_bench()` repeatedly performs session setup and logoff on one connection.
- `run_chain1()` and `run_chain2()` submit chained SMB1 requests for open/write/close and guest session setup/tree connect.
- `run_notify_bench()` combines repeated notify reads with parallel create/delete operations, optionally across multiple UNC targets from `-b`.
- `run_mangle1()` and `run_mangle_illegal()` validate short-name access and illegal-character POSIX-created file handling through Windows-style SMB names.
- `run_windows_write()` writes sparse-style blocks by writing the last byte first and pushing zero-filled data.
- `run_large_readx()` verifies SMB1 `CAP_LARGE_READX` reply sizes under normal and signing-required NT1 sessions.
- `run_msdfs_attribute()` checks that a named DFS link appears as both directory and reparse point.
- `run_cli_echo()` and `run_cli_splice()` test SMB echo and server-side/client-assisted copy semantics.
- `run_uid_regression_test()` checks bad UID/TID behavior after logoff and tree disconnect.
- `run_shortname_test()` verifies when short names should and should not be created for special characters.
- `run_tldap()` connects to LDAP/LDAPS/StartTLS as configured, performs SASL/GENSEC bind, paged search, complex-filter search, and extended-DN GUID formatting checks.
- `run_dir_createtime()` verifies directory create time and inode-return behavior across SMB1 and SMB2.
- `run_streamerror()` checks errors for querying and opening a stream on a directory.
- `run_pidhigh()` checks SMB1 PID high/low round-trip handling.
- `run_symlink_open_test()` verifies Windows open of a dangling POSIX symlink returns not-found errors instead of hanging.
- `run_smb1_wild_mangle_unlink_test()` and `run_smb1_wild_mangle_rename_test()` guard against wildcard/mangled-name operations touching the wrong POSIX-created file.
- `run_smb1_truncated_sesssetup()`, `run_smb1_negotiate_exit()`, `run_smb1_negotiate_tcon()`, and `run_ign_bad_negprot()` hand-build low-level SMB1 sequences for malformed or unusual negotiation/session/tree paths.

Important local test functions defined in this range:

- `run_local_substitute()` and `timesubst_test()` check `%` substitution and UTC time formatting.
- `run_local_base64()` round-trips random blobs from length 1 through 1999.
- `run_local_gencache()` checks string and blob cache set/get/delete behavior and type safety.
- `run_local_rbtree()` checks `db_open_rbt()` record store flags, updates, traversal, and deletion.
- `run_local_convert_string()` verifies `convert_string_error()` length and NUL-conversion behavior.
- `run_local_string_to_sid()`, `run_local_sid_to_string()`, and `run_local_binary_to_sid()` check SID parser rejection, formatting, and binary bounds.
- `split_ntfs_stream_name()`, `test_stream_name()`, and `run_local_stream_name()` specify the local canonicalization rules for NTFS stream names and `$DATA`.
- `run_local_memcache()` checks replacement, purge accounting, talloc ownership transfer, and leak-sensitive overwrite paths.
- `run_wbclient_multi_ping()` sends many asynchronous `WINBINDD_PING` requests across `torture_nprocs` winbind contexts.
- `run_local_dbtrans()` repeatedly increments a dbwrap record inside transactions in `transtest.tdb`.
- `run_local_tevent_poll()`, `run_local_hex_encode_buf()`, `run_local_remove_duplicate_addrs2()`, `run_local_tdb_opener()`, `run_local_tdb_writer()`, and `run_local_canonicalize_path()` cover focused utility behavior and stress loops.

The registry and harness use:

- `#define FLAG_MULTIPROC 1` to mark tests that should run through `create_procs()`.
- `torture_ops[]`, a name/function/flags table ending in `{ .name = NULL }`.
- `run_test()` to resolve a requested test name, run one test or recurse over all tests for `ALL`, time each run, and report failures.
- `main()` to parse the target UNC, options, credentials, and selected test names.

## Control Flow

Most individual tests follow the same pattern: open one or more `cli_state` connections, set socket options, clean any test paths from previous runs, create or query server state, assert exact `NTSTATUS` results or returned metadata, clean up files/directories, and close connections. Failure paths usually print a diagnostic and return `false`; many functions jump to an `out:` label so cleanup still runs.

The asynchronous notify/create-delete benchmark has a nested tevent flow. `run_notify_bench()` opens a directory, starts a repeating `swallow_notify_send()` request, starts `torture_createdels_send()` with ten parallel create/delete operations, and spins `tevent_loop_once()` until every configured share finishes. `torture_createdels_done()` keeps the pipeline full by replacing each completed subrequest with a new file name until the requested operation count is reached.

The large-read test creates a 20 MiB file, then runs two NT1 read scenarios: ordinary signing-if-required and signing-required. It negotiates a fresh connection for each scenario, optionally enables encryption or Unix extensions, opens the file read-only, and checks several request sizes through `check_read_call()`. `calc_expected_return()` constrains expected bytes by Unix large-read capability, signing, encryption, and SMB1 PDU overhead.

The LDAP test computes transport and GENSEC features from `client ldap sasl wrapping`, resolves the host, optionally upgrades to TLS or StartTLS, fetches RootDSE, binds with `torture_creds`, performs an asynchronous paged search, then validates complex search-filter parsing and extended-DN GUID formatting for control values absent, zero, and one.

The malformed SMB1 tests bypass high-level `cli_state` setup where needed. They resolve the host, open a raw TCP socket to port 445, wrap it in an `smbXcli_transport`, build an `smbXcli_conn`, negotiate a specific dialect, and send handcrafted SMB1 requests using `smb1cli_req_send()` or `smb1cli_session_setup_nt1_send()`.

At the harness level, `main()` initializes logging, locale, fault handling, loadparm state, interfaces, host/share parsing, defaults, and credentials. It parses options with `getopt()`, prompts for a password unless Kerberos or `-U user%pass` supplied one, initializes `torture_creds`, then calls `run_test("ALL")` or `run_test()` for each requested test argument. `run_test()` dispatches through `torture_ops[]`; tests marked `FLAG_MULTIPROC` run through `create_procs()`, which forks `torture_nprocs` children, synchronizes startup through anonymous shared memory, and aggregates child boolean results.

## State And Persistence Behavior

Network tests create transient files and directories on the selected SMB share. Examples include `\\notify-bench`, `\\MANGLE_ILLEGAL`, `\\writetest.txt`, `\\large_readx.dat`, `\\splice_src.dat`, `\\splice_dst.dat`, `\\uid_reg_test`, `\\shortname`, `\\testdir_createtime`, `\\testdir_streamerror`, `dangling_symlink`, and several SMB1 wildcard-mangle directories. Most tests explicitly unlink, remove directories, or call `torture_deltree()` before and after execution.

Some tests intentionally alter connection/session state: `run_sesssetup_bench()` repeatedly changes UID via session setup/logoff; `run_uid_regression_test()` mutates saved UID/TID values to check bad session behavior; `run_chain1()` and `run_chain2()` submit dependent SMB1 requests in a single chain; raw SMB1 tests leave normal `cli_state` flows and manage lower-level `smbXcli_conn` objects directly.

Local tests persist or mutate process-local and filesystem state. `run_local_gencache()` installs a global memcache via `memcache_set_global()`. `run_local_dbtrans()` creates and repeatedly updates `transtest.tdb`. `run_local_tdb_opener()` and `run_local_tdb_writer()` loop forever against `test.tdb` by design, making them stress/debug tests rather than normal finite regression checks. `timesubst_test()` temporarily sets `TZ=UTC` and restores the original timezone only when one was present.

Global harness variables configured in `main()` and earlier file scope affect this range: `host`, `share`, `username`, `password`, `workgroup`, `myname`, `sockops`, `torture_numops`, `torture_nprocs`, `torture_blocksize`, `test_filename`, `use_kerberos`, `do_encrypt`, `use_multishare_conn`, `multishare_conn_fname`, `signing_state`, and `torture_creds`.

## Dependencies And Integration Points

This chunk integrates with several Samba subsystems:

- SMB client libraries: `cli_state`, SMB1 request builders, SMB2-capable open/query helpers, signing/encryption state, transport creation, dialect negotiation, and tree/session helpers.
- POSIX extension client APIs: `torture_setup_unix_extensions()`, `cli_posix_open()`, `cli_posix_unlink()`, `cli_posix_symlink()`, and `cli_posix_mkdir()`.
- Event and async infrastructure: `tevent_context`, `tevent_req`, callback-data helpers, request polling, and loops.
- LDAP stack: `tldap_context`, RootDSE fetch, paged search, controls, TLS tstreams, StartTLS, and GENSEC SASL wrapping.
- Samba utility libraries: talloc, DATA_BLOB, base64, gencache, memcache, dbwrap, TDB, rb-tree DB, SID parsing/formatting, charset conversion, address de-duplication, path canonicalization, and time formatting.
- Winbind client stack: `wb_context`, `wb_trans_send()`, `wb_trans_recv()`, and `WINBINDD_PING`.
- Loadparm and runtime configuration: `loadparm_init_s3()`, `lp_load_global()`, `lpcfg_set_cmdline()`, `lpcfg_set_option()`, `lp_client_smb_transports()`, `lp_workgroup()`, and `SMB_CONF_PATH`.

The test table also references many functions defined outside this exact line range, including locking, oplock, POSIX ACL, SMB2, DFS, cleanup, messaging, g-lock, idmap, quota, path, and RPC-scale tests. The table is therefore the central integration point for the whole file, not only for functions defined in this chunk.

## Risks And Maintenance Notes

- The file is explicitly legacy: `usage()` warns that the Samba4 torture suite is more complete. New coverage may belong in the modern torture suite unless this exact source3 client path is required.
- Many tests are environment-sensitive. They depend on server dialect support, SMB1 availability, POSIX extensions, DFS links, LDAP/LDAPS configuration, credentials, winbind availability, signing/encryption policy, and share filesystem semantics.
- Several tests assume clean share paths and can fail if previous runs left files behind, cleanup failed due to permissions, or parallel users share the same target.
- SMB1-specific tests can fail or be inapplicable when SMB1 is disabled, when port 445 is blocked, or when a server rejects old dialects before the intended edge case.
- `run_large_readx()` has subtle expected-size logic around large-read capability, signing, encryption, and Windows server behavior. Changes to client buffer constants or SMB1 signing/encryption behavior can produce false regressions if the expected PDU math is not updated.
- Name-mangling tests depend on POSIX-created names that are illegal or wildcard-like from a Windows SMB perspective. A bug here can delete or rename the wrong file, so cleanup paths and test directories need to stay tightly scoped.
- `run_local_dbtrans()`, `run_local_tdb_opener()`, and `run_local_tdb_writer()` are unbounded loops in normal success flow. They should be invoked intentionally, usually under supervision or a timeout.
- `run_wbclient_multi_ping()` passes `&i` as callback data while also using `i` as loop and completion counter. This is intentional in the current code path but is easy to misread and fragile if the surrounding loop structure changes.
- `timesubst_test()` restores `TZ` only if it was originally present; if no `TZ` existed, the process remains with `TZ=UTC` for later tests in the same run.
- `create_procs()` forks children that open connections and run test functions. Tests used with `FLAG_MULTIPROC` must tolerate concurrent access to the same share and global path patterns.

## Test Signals

The primary test signal is the `smbtorture` process exit code: `main()` returns `0` only if every selected `run_test()` call returns true. For individual tests, useful positive signals are exact `NTSTATUS` matches, no unexpected diagnostics, cleanup completion, and the printed timing line `<TEST> took <secs> secs`.

Representative targeted invocations from this chunk include:

```sh
smbtorture //server/share -U user%pass DIR1
smbtorture //server/share -U user%pass SESSSETUP_BENCH
smbtorture //server/share -U user%pass CHAIN1 CHAIN2
smbtorture //server/share -U user%pass NOTIFY-BENCH
smbtorture //server/share -U user%pass MANGLE1 MANGLE-ILLEGAL
smbtorture //server/share -U user%pass LARGE_READX
smbtorture //server/share -U user%pass SMB1-TRUNCATED-SESSSETUP SMB1-NEGOTIATE-EXIT
smbtorture //server/share LOCAL-SUBSTITUTE LOCAL-BASE64 LOCAL-RBTREE LOCAL-MEMCACHE LOCAL-CANONICALIZE-PATH
```

Expected focused assertions include:

- `DIR1` sees the expected directory listing counts for wildcard and must-have attribute filters.
- `LARGE_READX` prints success only after all requested read lengths return the calculated or Windows-capped sizes.
- `MSDFS-ATTRIBUTE` requires `-f` to name a DFS link and expects `FILE_ATTRIBUTE_REPARSE_POINT` plus `FILE_ATTRIBUTE_DIRECTORY`.
- `WINDOWS-BAD-SYMLINK` accepts only `NT_STATUS_OBJECT_NAME_NOT_FOUND` or `NT_STATUS_OBJECT_PATH_NOT_FOUND`.
- `SMB1-WILD-MANGLE-UNLINK` and `SMB1-WILD-MANGLE-RENAME` verify the non-wildcard sibling remains present after Windows operations on a mangled wildcard-like name.
- `PIDHIGH` requires the returned SMB1 header PID low/high fields to be `0xBEEF` and `0xDEAD`.
- Local SID tests reject malformed SIDs and round-trip accepted strings exactly.
- Local stream-name tests define accepted forms such as `bla`, `bla::$DATA`, `bla:$DATA`, `bla:x:$DATA`, and `bla:x`, and reject invalid explicit stream types.

For build or harness validation, the important structural signal is that every `torture_ops[]` entry has a non-NULL function pointer until the sentinel and that `usage()` lists the same names that `run_test()` can dispatch.
