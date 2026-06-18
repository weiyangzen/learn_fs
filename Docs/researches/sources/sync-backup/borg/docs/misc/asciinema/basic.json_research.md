# sources/sync-backup/borg/docs/misc/asciinema/basic.json

## Purpose

`basic.json` is an asciinema v2 terminal recording used by the Borg documentation to introduce basic Borg 1.2.1 workflows. It records a guided shell session showing help output, repository initialization, creation of several compressed backups, deduplication behavior after adding a file and moving a directory, archive listing, targeted extraction, verification with `diff`, and remote repository initialization over SSH.

The file is documentation data rather than source code. Its job is to preserve a reproducible terminal demonstration for playback in docs, not to execute commands at build time.

## Important APIs, Types, and Data Shape

The first JSON value is the asciinema header:

- `version`: `2`.
- `width`: `80`.
- `height`: `24`.
- `timestamp`: `1657142858`.
- `env`: `{"SHELL": "/bin/bash", "TERM": "vt100"}`.

Every following line is an asciinema event array `[time_offset_seconds, stream, data]`. This file contains only output events with stream `"o"`. The recording has 2,647 events, ends around 162.062134 seconds, and stores about 16,827 bytes of output payload.

The demonstrated Borg CLI surfaces are:

- `borg help`.
- `borg init --encryption=repokey /media/backup/borgdemo`.
- `borg create --stats --progress --compression lz4 /media/backup/borgdemo::backupN Wallpaper`.
- `borg list /media/backup/borgdemo`.
- `borg list /media/backup/borgdemo::backup3 | grep 'deer.jpg'`.
- `borg extract /media/backup/borgdemo::backup3 Wallpaper/deer.jpg`.
- `borg init --encryption=repokey borgdemo@remoteserver.example:./demo`.

Supporting shell commands include `echo`, `mv`, `grep`, and `diff -s`.

## Control Flow and Recorded Scenario

The recording opens with comments explaining that it is a beginner teaser made with Borg 1.2.1. It runs `borg help` and captures the top-level Borg CLI usage, common options, and command list.

The first repository operation initializes `/media/backup/borgdemo` with `--encryption=repokey`. The session records passphrase prompts, a compatibility warning about older Borg versions up to 1.0.8, a suggested `borg upgrade --disable-tam` command for old-version compatibility, and a key/passphrase backup warning.

The first backup command creates `backup1` from the `Wallpaper` directory using `--stats`, `--progress`, and `--compression lz4`. The output reports 31 files, about 401.15 MB original size, 399.74 MB compressed size, and about 399.55 MB deduplicated size.

The user then adds `Wallpaper/newfile.txt` with `echo "new nice file"` and creates `backup2`. Borg reports 32 files but only 604 B of new deduplicated data, demonstrating chunk-level deduplication for mostly unchanged content.

The demo then moves `Wallpaper/bigcollection` to `Wallpaper/bigcollection_NEW` and creates `backup3`. The archive still represents about 401.15 MB of data, but only 550 B of deduplicated size is added, demonstrating that Borg recognizes moved directory content and does not duplicate file chunks just because paths changed.

The restore portion lists the repository, showing `backup1`, `backup2`, and `backup3` with timestamps and fingerprints. It lists the contents of `backup3` filtered for `deer.jpg`, renames the local `Wallpaper` directory to `Wallpaper.orig`, extracts `Wallpaper/deer.jpg` from `backup3`, and verifies the restored file with `diff -s`, which reports the files are identical.

Finally, the recording demonstrates initializing a remote repository with `borg init --encryption=repokey borgdemo@remoteserver.example:./demo`, again showing passphrase prompts, security compatibility text, and the key backup warning. It closes by pointing users to the advanced screencast.

## State and Persistence Behavior

The JSON file persists the terminal recording only. Inside the recorded scenario, the commands demonstrate these state changes:

- `borg init --encryption=repokey` creates encrypted repository metadata and key material in the target repository.
- Repeated `borg create` calls append immutable archives named `backup1`, `backup2`, and `backup3`.
- Borg's cache and chunk index track already-seen file content so later archives can have large logical sizes but tiny deduplicated sizes.
- `echo` and `mv` mutate the source `Wallpaper` tree between backup runs.
- `borg list` is read-only.
- `borg extract` writes restored content back to the working tree.
- `diff -s` is read-only and provides a verification signal.
- The remote `borg init` would create a repository on a remote SSH target if executed against a real server.

As an asciinema artifact, event order and timing are the state. Consumers should not attempt to infer command success by executing the strings; they should replay or inspect the serialized output.

## Dependencies and Integration Points

The data-level dependency is the asciinema v2 JSON-line format. It likely integrates with Borg documentation pages or static assets under `docs/misc/asciinema/`, where a web player can fetch and replay it.

The demonstrated command-level dependencies are Borg 1.2.1, bash, an accessible `/media/backup/borgdemo` path, a `Wallpaper` directory with demo files, local filesystem permissions, `grep`, `diff`, and SSH/Borg setup on `remoteserver.example` for the remote example. The remote host is clearly illustrative; the recording captures the intended command form, not a reusable live endpoint.

## Risks and Edge Cases

- The cast is version-specific. Borg help text, security warnings, output tables, progress formatting, and archive fingerprints may differ in other versions.
- The repository path `/media/backup/borgdemo`, `Wallpaper` data set, and remote host are demo-specific. Executing the commands directly on another machine can fail or mutate unintended data.
- `--encryption=repokey` requires users to back up key material and remember the passphrase. The recording includes this warning, but automated docs extraction should avoid shortening it away.
- The output stream includes passphrase prompts without typed secret input. Replay tools should preserve the prompts without inventing input events.
- Progress output is carriage-return heavy and may appear as dense repeated status text when rendered as plain logs.
- The recording demonstrates `grep 'deer.jpg'` filtering; if source demo data changes, the transcript and verification narrative would no longer match.

## Test Signals

Validation should cover both serialization and content:

- Parse as newline-delimited JSON with an asciinema v2 header and output event rows.
- Confirm all event rows have numeric offsets, stream `"o"`, and string payloads.
- Confirm the final offset is around 162.062134 seconds and timestamps do not move backward.
- Join output payloads and check for anchor commands: `borg help`, local `borg init`, three `borg create` commands, `borg list`, `borg extract`, `diff -s`, and remote `borg init`.
- Check narrative anchors such as `Archive name: backup1`, `Archive name: backup2`, `Archive name: backup3`, the tiny deduplicated sizes for the second and third backups, and `Files Wallpaper/deer.jpg and Wallpaper.orig/deer.jpg are identical`.
- Replay with an asciinema player to catch malformed JSON-line content or terminal rendering regressions.
