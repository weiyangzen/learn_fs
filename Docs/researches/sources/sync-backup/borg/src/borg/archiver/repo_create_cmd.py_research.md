# sources/sync-backup/borg/src/borg/archiver/repo_create_cmd.py

## Purpose

`repo_create_cmd.py` implements `borg repo-create`, creating a new empty repository, selecting encryption/key storage, optionally deriving related repository key material from another repository, initializing the manifest, and creating the initial cache. The source was read as a complete 243-line file.

## Important APIs, Types, and Functions

`RepoCreateMixIn.do_repo_create()` is wrapped with `with_repository(create=True, exclusive=True, manifest=False)` and `with_other_repository(manifest=True, compatibility=READ)`. It calls `key_creator()`, constructs `Manifest`, writes it, opens `Cache` once, and prints key backup and reserve-space guidance. `build_parser_repo_create()` registers `--other-repo`, `--from-borg1`, required `--encryption`, `--key-location`, and `--copy-crypt-key`, with encryption choices from `key_argument_names()`.

## Control Flow

The command opens/creates the target repository and optionally an already existing other repository. If an other manifest exists, its key is passed to `key_creator()` and may have `copy_crypt_key` set. On passphrase EOF or keyboard interrupt, the partially created repository is destroyed and `CancelledByUser` is raised. Otherwise it writes a new manifest with the created key, initializes the cache with `warn_if_unencrypted=False`, warns about backing up key/passphrase for non-plaintext modes, and recommends reserving emergency repository space.

## State and Persistence Behavior

This command creates persistent repository storage, key material in either repository or keyfile location, a manifest object, and local cache/security metadata. Cancellation before key creation completion destroys the target repository. Related repository creation can persist shared ID/chunker secret material, and optionally shared crypt key, enabling dedup/transfer workflows.

## Dependencies and Integration Points

It integrates with repository creation wrappers, key creation and key argument registries, `Location` validation, optional other-repository access, `Manifest`, `Cache`, and reserve-space guidance implemented by `repo_space_cmd.py`. It is the root lifecycle command for repositories later used by create, key, info, and delete commands.

## Risks and Edge Cases

Encryption mode is required and cannot be changed later; only key storage can move later. Related repositories need careful crypt-key copying decisions. Passphrase cancellation must destroy incomplete repositories to avoid unusable leftovers. Plaintext mode suppresses key backup warning but still creates a repository with different security assumptions. Remote/sftp stores can be slow because underlying borgstore pre-creates directories.

## Test Signals

Tests should cover each encryption/key-location parser choice, plaintext versus encrypted warning behavior, cancellation cleanup, initial manifest/cache creation, related repository key material reuse with and without `--copy-crypt-key`, `--from-borg1` argument propagation, required encryption validation, and reserve-space warning output.
