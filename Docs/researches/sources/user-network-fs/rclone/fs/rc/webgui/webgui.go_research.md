# sources/user-network-fs/rclone/fs/rc/webgui/webgui.go

## Purpose
This file provides WebGUI release download, update, unzip, path creation, and GitHub release JSON helpers.

## Important APIs, Types, and Functions
- `GetLatestReleaseURL(fetchURL)` fetches GitHub release metadata and returns first asset download URL, tag, and size.
- `CheckAndDownloadWebGUIRelease(checkUpdate, forceUpdate, fetchURL, cacheDir)` manages cached WebGUI installation and updates.
- `DownloadFile(filepath, url)` streams an HTTP 200 response to a local file.
- `Unzip(src, dest)` extracts a zip archive while checking for Zip Slip paths.
- `exists` and `CreatePathIfNotExist` are filesystem helpers.
- `gitHubRequest` models the GitHub releases API payload fields used here.

## Control Flow
Update flow computes `cacheDir/webgui`, `tag`, and `current` paths, validates directories, fetches latest release metadata, compares the cached tag file, and downloads/extracts when missing, update requested, or forced. Zip files are removed after extraction and the tag file is written.

## State and Persistence
The WebGUI cache persists under `cacheDir/webgui`, including `current`, release tag file, and temporary release zip. Downloads and extraction mutate local filesystem state.

## Dependencies and Integration Points
It depends on standard `archive/zip`, `net/http`, and filesystem packages plus rclone `fs` logging and `lib/file`. `rcserver.newServer` calls `CheckAndDownloadWebGUIRelease` when `--rc-web-gui` is enabled; plugin install code reuses `DownloadFile`, `Unzip`, and `CreatePathIfNotExist`.

## Risks and Edge Cases
`GetLatestReleaseURL` blindly selects the first asset, so release asset ordering matters. There is no hash/signature verification despite a TODO. `DownloadFile` overwrites/creates the target path directly. `Unzip` protects against paths outside `dest`, but archive size and file count are not bounded here. Update checks require live network access even when an existing install is present.

## Test Signals
No direct tests for this file are listed in the subset. WebGUI plugin RC tests exercise `DownloadFile` and `Unzip` indirectly through plugin installation; RC server WebGUI paths are not deeply tested here.
