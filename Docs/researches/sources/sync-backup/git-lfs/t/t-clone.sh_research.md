# sources/sync-backup/git-lfs/t/t-clone.sh

## Purpose
Large integration suite for `git lfs clone` and regular `git clone` with LFS smudge. It covers HTTP, SSL, client certificates, clone flags, include/exclude filters, `.lfsconfig`, missing clean filters, recursive submodules, current-directory clone, empty repositories, bare clones, and cookie-based authentication.

## Important APIs, Functions, and Control Flow
Tests create remotes, track `*.dat`, generate deterministic file histories with `lfstest-testutils addcommits`, push, then clone through several modes. SSL and client-certificate tests configure certificate paths and credential records. Flag tests exercise `--template`, `--local`, `--no-checkout`, `--branch`, `--origin`, `--separate-git-dir`, `--bare`, and short options. Include/exclude and `.lfsconfig` tests assert selective object download. Submodule tests build nested repositories with LFS content.

## State, Persistence, and Dependencies
The script mutates global SSL and credential config, `CREDSDIR`, HOME certificate copies, remote URLs, cookie files, submodule metadata, hooks, and LFS object stores. Dependencies include credential helper `lfstest`, certificate fixtures, `assert_hooks`, object assertions, and Git version gating.

## Integration Points, Risks, and Test Signals
Integration covers clone wrapper behavior, smudge downloads, hook installation, Git config precedence, TLS client auth, cookies, submodules, and fetch include/exclude logic. Signals are clone logs, downloaded file sizes, object-store counts, clean status, hook assertions, and absence of filter/error lines. Risks include global config leakage, platform-specific certificate paths, and deprecation-sensitive `git lfs clone` behavior.
