<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs.c_research.md`. Source lines read for this pass: 662.

## Purpose
General eCryptfs mount helper used by `/bin/mount` to gather/validate mount options, manage signature cache warnings, and invoke the real mount command.

## Important APIs, Types, And Functions
Important functions: `parse_arguments`, `strip_userland_opts`, `process_sig`, `opts_str_contains_option`, `ecryptfs_validate_mount_opts`, `ecryptfs_mount`, `ecryptfs_do_mount`, and `main`.

## Control Flow
Locks future memory, validates user and keyring, parses source/target/options, toggles verbosity/signature-cache behavior, runs `ecryptfs_process_decision_graph` unless remounting, appends `ecryptfs_unlink_sigs`, prompts about unknown signatures, validates required `ecryptfs_key_bytes`, canonicalizes paths, and forks `/bin/mount -i --no-canonicalize -t ecryptfs`.

## State And Persistence Behavior
May create `~/.ecryptfs/sig-cache.txt` and append signatures. Mount state is delegated to `/bin/mount` and the kernel.

## Dependencies And Integration Points
Depends on libecryptfs decision graph, keyutils, libgcrypt, sysfs version detection, passwd home lookup, and `/bin/mount`.

## Risks And Edge Cases
Mount option parsing and string scrubbing are security-sensitive. Unknown options intentionally pass through to the kernel, while userland options must not. Signature-cache prompts can block automation unless `no_prompt`/verbosity options are set.

## Test Signals
Exercise interactive and `-o` modes, `no_sig_cache`, `no_prompt`, FNEK options, unknown options, missing key bytes, and remount rejection.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/mount.ecryptfs.c -->
