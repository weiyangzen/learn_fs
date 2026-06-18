<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-torrent -->
# sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-torrent

Purpose: demonstration external special remote that downloads content from torrent URLs using `aria2c`, with support for single-file and multi-file torrent metadata.

Important functions: `runcmd` preserves stdout protocol cleanliness. `getvalue` and `geturls` retrieve known torrent URLs for a key. `istorrent` matches URLs ending in `.torrent` plus optional `#N` file selector. `downloadtorrent` creates a temp directory, uses `btshowmetainfo` to discover wanted file paths, runs `aria2c`, moves the selected file to the requested destination, and removes temp state.

Control flow: emits `VERSION 2`. `INITREMOTE` and `PREPARE` succeed. `CLAIMURL` accepts torrent URLs. `CHECKURL` downloads a torrent file with restricted curl protocols, inspects metadata, and emits `CHECKURL-MULTI` entries for each file or a single entry. `TRANSFER STORE` is unsupported. `TRANSFER RETRIEVE` selects a known torrent URL, downloads the `.torrent`, derives the selected file number, downloads content, and reports success or failure. `CHECKPRESENT` reports unknown. `REMOVE` emits `SETURLMISSING` for all known torrent URLs and succeeds.

State and persistence: transient temp files and directories are created for torrent metadata and downloads. Persistent state is only the git-annex URL metadata modified by `SETURLMISSING`.

Dependencies and integration points: POSIX shell, `curl`, `aria2c`, `btshowmetainfo`, `mktemp`, `grep`/`egrep`, `sed`, `expr`, and git-annex's external special remote URL protocol.

Risks: no resume support and no progress reporting. Multi-file torrent parsing assumes `btshowmetainfo` output and normalizes spaces to underscores in `CHECKURL-MULTI`, so exact names with spaces are lossy. The `filenum` extraction uses a sed pattern that appears to use `\d`, which is not portable POSIX sed and may fail to extract the fragment. Torrent downloads can fetch extra pieces/files.

Test signals: use fixture torrent metadata for single and multi-file cases, test `CHECKURL-MULTI`, retrieve a selected file, reject upload, remove URL metadata, and exercise filenames with spaces and failed downloads.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/external/git-annex-remote-torrent -->
