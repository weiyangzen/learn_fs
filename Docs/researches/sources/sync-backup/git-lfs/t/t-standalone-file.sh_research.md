<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-standalone-file.sh -->
# sources/sync-backup/git-lfs/t/t-standalone-file.sh

Purpose: exercises the standalone file transfer adapter used for local `file://` remotes and local paths, including upload/download, clone, missing-object failure, `lfs.url` overrides, HTTP fallback, and invalid local repositories.

Important APIs/functions: defines `do_upload_download_test` and `do_local_path_test`; uses `git lfs track`, `lfstest-testutils addcommits`, `git push`, `git lfs fetch --all`, `git lfs fsck`, `native_path`, `urlify`, and trace assertions for `xfer: started custom adapter process`.

Control flow: upload/download helper creates many LFS objects, pushes via local file remote, compares local and remote object lists, deletes local media, and fetches all objects back. Local path helper clones using absolute Unix-style, relative, and native paths. Dedicated tests cover bare and non-bare remotes, missing remote file continuation, clone from file URL, local path/trailing slash behavior, `lfs.url` pointing to file or HTTP endpoints, and an invalid non-repo path error.

State and persistence: creates bare and non-bare Git repositories on disk, writes LFS object files directly under those repos, removes local object stores, and modifies `remote.origin.url` and `lfs.url`.

Dependencies and integration points: integrates with custom transfer adapter discovery, file URL/path normalization, local object store layout, HTTP endpoint override behavior, and fsck validation.

Risks: path handling is platform-sensitive, especially Windows/native paths and trailing slashes. Failure semantics must download all available objects while surfacing missing files, and `lfs.url` must not accidentally write to the Git remote when overridden.

Test signals: nine integration blocks cover bare/non-bare local remotes, missing files, clone, path variants, file/HTTP `lfs.url`, and invalid remote errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-standalone-file.sh -->
