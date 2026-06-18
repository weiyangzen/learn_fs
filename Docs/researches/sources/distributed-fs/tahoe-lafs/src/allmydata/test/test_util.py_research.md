# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_util.py

## Purpose
This module tests a broad set of Tahoe utility helpers: id encoding, significant-figure rounding, file and path operations, polling, YAML loading, JSON encoding for bytes, remote-reference version enrichment, and CPU thread-pool dispatch.

## Important APIs, Types, And Functions
`IDLib` covers `idlib.nodeid_b2a`. `Math` covers `mathutil.round_sigfigs`. `FileUtil` covers `fileutil.make_dirs`, `rm_dir`, `remove_if_possible`, `write_atomically`, `rename`, `rename_no_overwrite`, `replace_file`, `du`, `abspath_expanduser_unicode`, `to_windows_long_path`, `make_dirs_with_absolute_mode`, `windows_expanduser`, `get_available_space`, `get_disk_stats`, `get_pathinfo`, `EncryptedTemporaryFile`, and `write`. `PollMixinTests` covers `pollmixin.PollMixin.poll`. `YAML` covers `yamlutil.safe_load`. `JSONBytes` covers `jsonbytes.dumps`, `dumps_bytes`, `loads`, `UTF8BytesJSONEncoder`, and `AnyBytesJSONEncoder`. `RrefUtilTests` uses `FakeGetVersion` plus `LocalWrapper` to test `rrefutil.add_version_to_remote_reference`. `CPUThreadPool` covers `defer_to_thread` and `disable_thread_pool_for_test`.

## Control Flow
File tests build temporary directories/files, mutate permissions, perform atomic writes and renames, and assert resulting contents and existence. Path tests exercise unicode path expansion, Windows long-path translation, platform-specific drive handling, long path creation, user home expansion, disk-space calculations, symlink metadata, and absent-path metadata. Poll tests run immediate-success, delayed-success, and timeout cases. JSON tests encode nested bytes/unicode structures, assert UTF-8 decoding by default, assert non-UTF-8 failures unless `any_bytes` is enabled, and confirm bytes output for `dumps_bytes`.

Remote-reference tests wrap a fake object whose `remote_get_version` either returns a value or raises Foolscap exceptions; successful calls attach the reported version while failures attach the default. CPU thread-pool tests compare thread identities to ensure normal dispatch leaves the current thread and disabled dispatch stays in the current thread.

## State And Persistence
State is limited to temporary filesystem trees, permissions, symlinks, environment-like patches of `fileutil.windows_getenv`, and thread identity observations. No durable repository data is intentionally persisted. The module explicitly cleans long-path files and relies on Trial temporary paths for many writes.

## Dependencies And Integration Points
The module integrates Tahoe utility modules with Twisted Trial, Foolscap `Violation`/`RemoteException`, YAML and JSON libraries, local no-network wrappers, and thread-pool helpers. It is a cross-platform regression suite for utility behavior that many Tahoe subsystems rely on, especially path handling and JSON serialization.

## Risks And Test Signals
Signals include idempotent directory removal, non-overwriting rename semantics, conflict-safe replacement, unicode and Windows path behavior, disk-stat nonnegative availability, symlink metadata, JSON bytes policy, remote-version fallback, and test-time thread-pool disable behavior. Risks are platform sensitivity around permissions, long paths, symlinks, filesystem timestamp/encoding behavior, and disk-space assumptions.
