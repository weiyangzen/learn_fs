# sources/security-integrity/encfs/tests/encfsr_live_test.rs

Purpose: ignored live FUSE tests for `encfsr`, the reverse-mode binary backed by `ReverseFs`. It verifies encrypted virtual namespace behavior and ciphertext compatibility by mounting `encfsr` and, in round-trip cases, mounting forward `encfs` on top of the reverse mount.

Important APIs/types/functions: `make_encfsr_config`, `setup_source_dir`, `EncfsrMountGuard::mount`, `make_encfsr_config_with_mac`, `setup_block_boundary_files`, and `live_config_from_encfs` create fixtures and manage child processes. Tests include encrypted readdir, stat ciphertext sizing, EROFS writes, path resolution, V6 block-boundary round-trip, virtual `.encfs7`, external IV chaining, V7 AES-GCM-SIV round-trip, symlink round-trip, and multi-GB streaming.

Control flow: the guard checks `ENCFS_LIVE_TESTS`, unmount tools, spawns `encfsr --foreground --stdinpass`, drains output, writes password, polls `/proc/self/mountinfo`, and unmounts on drop. Tests create plaintext source directories, save configs, mount reverse view, inspect encrypted names or bytes, and optionally use `live::MountGuard` as a decrypting mount.

State and persistence: creates temp source and mount directories, writes configs and plaintext fixtures, and removes temp roots. Runtime process state is guarded by a global live lock.

Dependencies and integration points: depends on FUSE availability, Cargo `encfsr` binary, `/proc/self/mountinfo`, unmount tools, `EncfsConfig`, `SslCipher`, `BlockLayout`, and the shared live forward-mount harness.

Risks: ignored tests require privileges/environment and can be slow; the multi-GB test needs substantial disk and time. Mount readiness depends on Linux mountinfo and path canonicalization. Some assertions assume root directory IV 0 and known config properties.

Test signals: strongest end-to-end signal for `ReverseFs` correctness, especially streaming encrypted reads, read-only semantics, metadata sizing, V6/V7 compatibility, and symlink/config virtual file behavior.
