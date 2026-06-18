# sources/sync-backup/borg/docs/misc/asciinema/advanced.json

## Purpose

`advanced.json` is an asciinema v2 terminal recording used by the Borg documentation to demonstrate advanced Borg 1.2.1 usage. It records a scripted shell session in an 80x24 `vt100` terminal running `/bin/bash`. The session assumes an existing Borg repository at `/media/backup/borgdemo` and shows how a more experienced user can rely on environment variables, placeholder-based archive names, alternate compression settings, stdin backups, repository inspection, key export, consistency checks, pruning, archive diffs, tar export, and FUSE mounting.

The file is data, not application code. Its runtime purpose is to be consumed by asciinema-compatible players or documentation build steps so users can replay the session with original timing and terminal output.

## Important APIs, Types, and Data Shape

The top-level format follows asciinema v2:

- Header object: `{"version": 2, "width": 80, "height": 24, "timestamp": 1657143034, "env": {"SHELL": "/bin/bash", "TERM": "vt100"}}`.
- Event rows: arrays shaped as `[time_offset_seconds, stream, data]`.
- Stream values: only output stream `"o"` is present in this file.
- `data` values contain terminal bytes as JSON strings. Many events contain one character; others contain larger command output chunks, progress redraws, ANSI-style terminal spacing, prompts, and CRLF boundaries.

The recording has 3,868 event rows, a final event timestamp around 188.567499 seconds, and about 95,407 bytes of output payload. Consumers must process it as newline-delimited JSON values, not as one JSON array.

The main external CLI surfaces demonstrated are:

- `BORG_REPO` and `BORG_PASSPHRASE` environment variables.
- `borg create` with `--stats`, `--progress`, `--compression`, archive placeholders like `::{user}-{now}`, `--exclude`, and stdin input via `-`.
- `borg info :: --last 1`.
- `borg rename ::specialbackup backup-block-device`.
- `borg key export --qr-html :: file.html` and `borg key export --paper ::`.
- `borg check -v ::`.
- `borg prune --list --keep-last 1 --dry-run`.
- `borg diff ::backup1 backup2`.
- `borg export-tar --progress ::backup2 backup.tar.gz`.
- `borg mount :: /tmp/mount` and `borg umount /tmp/mount`.

## Control Flow and Recorded Scenario

The terminal narrative starts by warning that the cast was made with Borg 1.2.1 and that other versions may differ. It then configures `BORG_REPO=/media/backup/borgdemo` and `BORG_PASSPHRASE=1234`, which allows later Borg commands to use the compact `::archive` syntax and skip repeated passphrase prompts.

The advanced creation section creates a backup with `borg create --stats --progress --compression lz4 ::{user}-{now} Wallpaper`. Borg expands the placeholders into an archive named `root-2022-07-06T21:31:12`; the output reports 32 files, about 401.15 MB original size, and only 542 B of deduplicated size because the repository already contains matching content from the basic demo.

The recording then creates a separate archive for `~/Downloads` using `--compression zlib,6` and `--exclude ~/Downloads/big`. The demonstrated run captures no files and reports a 576 B original payload, but it still illustrates mixing source trees and compression policies in the same deduplicated repository.

Next, the cast pipes a block device through stdin: `sudo dd if=/dev/loop0 bs=10M | borg create --progress --stats ::specialbackup -`. The `dd` output shows 419,430,400 bytes copied; Borg stores one stdin-backed archive, with heavy compression and deduplication reducing the new deduplicated size to roughly 33 kB in this demo.

The useful-commands section inspects the most recent archive with `borg info :: --last 1`, renames `specialbackup` to `backup-block-device`, and verifies the renamed archive with another `borg info` call. The archive fingerprint changes after rename while archive metadata such as start/end time and command line remain associated with the original creation command.

The key-management section exports repository key material in two forms: a QR HTML file and a paper key. The paper-key output is intentionally visible in the recording, including `BORG PAPER KEY v1` rows. This is useful as documentation but sensitive as example content if copied into real workflows.

The maintenance section runs `borg check -v ::`, which records repository, index, and archive consistency checks across six archives. It then performs a dry-run prune with `--keep-last 1`, keeping `backup-block-device` and showing five older archives that would be removed.

The restore/export section uses `borg diff ::backup1 backup2` to show `Wallpaper/newfile.txt` as a 14-byte addition, exports `backup2` to `backup.tar.gz` with progress, lists the working directory, mounts the whole repository at `/tmp/mount`, lists archive directories under the mount point, and unmounts it. The mount/ls/unmount output is interleaved in terminal-capture order, so replay correctness depends on preserving the exact event stream.

## State and Persistence Behavior

This file persists only the recording, not Borg repository state. The recorded commands demonstrate persistent Borg effects:

- `BORG_REPO` and `BORG_PASSPHRASE` affect the shell process and all following Borg invocations in the session.
- `borg create` appends archives and chunk/index metadata to `/media/backup/borgdemo`.
- Archive placeholder expansion stores time- and user-derived archive names.
- `borg rename` mutates archive metadata and produces a new fingerprint for the renamed archive.
- `borg key export` writes `file.html` and emits paper key material.
- `borg prune --dry-run` deliberately does not mutate repository state.
- `borg export-tar` writes `backup.tar.gz`.
- `borg mount` creates a transient FUSE view under `/tmp/mount`; `borg umount` tears it down.

For the asciinema file itself, all state is immutable serialized terminal output. Any documentation player should treat timing offsets as replay metadata and strings as opaque terminal output, not as commands to execute.

## Dependencies and Integration Points

Primary data dependency is the asciinema v2 format. Integration points are likely Borg documentation pages that embed or link this recording, asciinema-player or compatible web components, and documentation build/static asset pipelines that copy files under `docs/misc/asciinema/`.

The demonstrated runtime dependencies include Borg 1.2.1, bash, `sudo`, `dd`, a loop device at `/dev/loop0`, a FUSE-capable environment for `borg mount`, `ls`, a repository initialized at `/media/backup/borgdemo`, and previously created archives from the basic screencast. The recording also assumes root-owned files and directories visible in the demo output.

## Risks and Edge Cases

- The recording hard-codes Borg 1.2.1 behavior, command output, fingerprints, timings, and archive names. Newer Borg versions may change help text, defaults, warnings, progress rendering, archive fingerprints, or command aliases.
- `BORG_PASSPHRASE='1234'` is intentionally insecure demo material. Documentation consumers should not treat it as recommended practice.
- The paper key block is example secret material. It is not useful for this repository outside the demo, but scanners may still flag it as key-like content.
- Asciinema event rows include carriage returns and progress redraws. Tools that line-split naively can misread progress sections or reorder mount output.
- The `export-tar --progress` portion dominates the payload and includes many repeated progress updates. This can make diffs noisy and can stress simplistic Markdown or log renderers if converted verbatim.
- `borg mount` requires platform support and may fail in CI or containerized environments; the recording should be replayed, not executed, during docs tests.

## Test Signals

Useful validation signals for this file are structural and transcript based:

- Parse as newline-delimited JSON; the first object must have `version: 2`, `width: 80`, and `height: 24`.
- All subsequent entries should be arrays of length 3 with a numeric timestamp, stream `"o"`, and string payload.
- Timestamps should be nondecreasing and end around 188.567499 seconds.
- A joined transcript should contain the expected advanced commands: `export BORG_REPO`, `borg create ... ::{user}-{now}`, stdin `dd | borg create`, `borg info`, `borg rename`, `borg key export`, `borg check`, `borg prune --dry-run`, `borg diff`, `borg export-tar`, `borg mount`, and `borg umount`.
- Replay in an asciinema-compatible player should show an 80x24 terminal with no JSON parse errors and with progress redraws preserved.
