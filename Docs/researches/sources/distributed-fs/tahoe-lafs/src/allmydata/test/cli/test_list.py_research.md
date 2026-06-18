# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_list.py

## Purpose
This module tests `tahoe ls` behavior for normal directories, missing entries, unrecoverable directories, direct filecaps, unknown caps, read-only alias listing, and JSON output for MDMF/SDMF/immutable nodes.

## Important APIs, Types, and Functions
- `List.test_list` builds a directory with Unicode entries, one-share and zero-share damaged subdirectories, unknown child caps, and direct filecap listing assertions.
- `List._create_directory_structure` creates a directory containing MDMF, SDMF, and immutable files for format tests.
- `test_list_readonly` checks `list-aliases --readonly-uri`.
- `test_list_mdmf` and `test_list_mdmf_json` assert human and JSON output include mutable formats and caps.

## Control Flow
The main test creates a dirnode via the test client, adds a Unicode file, creates damaged subdirectories by deleting shares, maps it to the `tahoe` alias, and runs `ls` variants. It then renames the Unicode child to ASCII to repeat key assertions independent of terminal encoding. Later it creates an immutable unknown child and checks both directory listing and direct unknown-cap listing. The MDMF helper creates mutable files with different versions and an immutable file, then links them into the directory before CLI listing.

## State and Persistence Behavior
Remote grid state is central: dirnodes, files, mutable nodes, damaged share sets, aliases, and unknown URI children. Local state is limited to test basedirs. Tests mutate the remote directory by moving a Unicode child to an ASCII name and by deleting shares to simulate unrecoverable objects.

## Dependencies and Integration Points
Dependencies include `upload.Data`, `MutableData`, `MDMF_VERSION`, `SDMF_VERSION`, `quote_output`, `GridTestMixin`, and `CLITestMixin`. The module integrates low-level node creation APIs with CLI listing, giving coverage of how web/API metadata is rendered by `ls`.

## Risks and Edge Cases
Risks include Unicode output conversion failures, missing path reporting, insufficient shares producing correct 410/Unrecoverable messages, direct filecap metadata without edge names, unknown objects still rendering with warnings, and JSON output preserving mutable format and cap fields. A suspicious detail is that `_create_directory_structure` assigns `_sdmf_uri = mdmf_node.get_uri()` instead of the SDMF node; tests may still pass due to broad string checks but this deserves attention if failures appear.

## Test Signals
The tests provide strong behavior signals through real grid objects, share deletion, CLI output checks, and JSON format/cap assertions. They also explicitly cover graceful missing alias errors.
