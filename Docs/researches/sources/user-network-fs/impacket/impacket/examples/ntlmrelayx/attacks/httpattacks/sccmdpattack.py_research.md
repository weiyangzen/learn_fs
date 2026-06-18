# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/sccmdpattack.py

## Purpose
`sccmdpattack.py` implements an SCCM Distribution Point relay attack that indexes packages exposed under `sms_dp_smspkg$`, builds a tree of package contents, and downloads files matching configured extensions or explicit URLs.

## Important APIs, Types, and Functions
- `print_tree()` writes a directory tree representation to an output stream.
- `PackageIDsRetriever(HTMLParser)` extracts package IDs from Datalib anchor tags.
- `FilesAndDirsRetriever(HTMLParser)` extracts directory/file links and associated previous text markers.
- `SCCMDPAttack._run()` orchestrates indexing and download.
- `recursive_file_extract()`, `download_files()`, `download_target_files()`, `handle_packages()`, `recursive_package_directory_fetch()`, and `fetch_package_ids_from_datalib()` implement package traversal and download.

## Control Flow
`_run()` derives the distribution point URL from client port/host, creates a timestamped loot directory, normalizes extension filtering, optionally fetches package IDs from Datalib, then calls `download_target_files()`. Explicit file mode reads URLs from `config.SCCMDPFiles`; otherwise it handles every discovered package by recursively fetching directory listings, writing `index.txt`, selecting matching files, creating package directories, and downloading each file.

## State and Persistence Behavior
Local state includes `distribution_point`, `loot_dir`, `package_ids`, and normalized config extension lists. Persistent output is a timestamped `*_sccm_dp_loot` directory with `index.txt` and downloaded package files under `packages/<package_id>/`. Remote state is read-only HTTP access.

## Dependencies and Integration Points
It depends on `os`, `json` (unused), `urllib.parse`, `HTMLParser`, `datetime`, and `impacket.LOG`. It is mixed into `HTTPAttack` and assumes `self.client.host`, `self.client.port`, `request()`, and `getresponse()`.

## Risks and Edge Cases
- HTML parsing depends on IIS directory listing shape and previous text containing `<dir>`.
- Recursive traversal uses a fixed max depth of 7; deeper packages are marked but not traversed.
- Output filenames are derived from URL path fragments and may collide.
- No HTTP status checks are performed before parsing/downloading bodies.
- Extension matching is suffix-based and case-sensitive.

## Test Signals
Unit tests should feed sample Datalib and directory HTML to the parsers, verify recursion depth handling, extension filtering, explicit URL mode, output path construction, and download request headers. Integration tests need an SCCM DP fixture or captured HTTP directory listings.
