<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/utable.c -->
# sources/user-network-fs/samba/source3/torture/utable.c

## Purpose
`utable.c` provides two smbtorture tests for server-side Unicode filename handling. `torture_utable()` probes which UTF-16 code points can be converted into Unix names, created through SMB1 client calls, and represented in 8.3 alternate names. `torture_casetable()` probes server case-folding/equivalence behavior by repeatedly creating single-character names and storing matching character sets in the file content.

## Important APIs, types, and functions
- `torture_utable(int)` opens a test SMB connection, creates `\utable`, iterates code points `1..0xffff`, converts each `smb_ucs2_t` with `convert_string(CH_UTF16LE, CH_UNIX, ...)`, creates a file with `cli_openx`, queries its short name with `cli_qpathinfo_alt_name`, and writes a 64 KiB `valid.dat` bitmap of characters whose alternate name is not the default `X_A_L...` pattern.
- `form_name(int)` converts one UTF-16 code point to a `\utable\<char>` path in a static `fstring`.
- `torture_casetable(int)` uses `cli_ntcreate`, `cli_qfileinfo_basic`, `cli_read`, and `cli_writeall` to discover which later character opens/aliases an existing earlier character on the server.

## Control flow
Both tests open a torture connection, recreate the `\utable` directory, loop through the Basic Multilingual Plane, and skip characters that fail charset conversion or SMB create/open. `torture_utable()` treats successful file creation as "allowed" and treats alternate names that differ from the common `X_A_L` prefix as meaningful short-name candidates. `torture_casetable()` creates or opens a single-character file using `FILE_OPEN_IF`; if the file already has content, that content is interpreted as previously matching code points, then the current code point is appended for future matches.

## State and persistence behavior
Remote state is temporary under the SMB share path `\utable` and is removed with `torture_deltree` or `cli_rmdir` at the end. Local state includes a generated `valid.dat` file in the process working directory and the in-memory `valid[0x10000]` bitmap or `equiv[0x10000][8]` table. The tests intentionally mutate remote files as probes rather than validating a pre-existing fixture.

## Dependencies and integration points
The file depends on smbtorture connection helpers from `torture/proto.h`, SMB client APIs from `libsmb/clirap.h`, Samba charset conversion, `fstring` helpers, NT status checks, and ordinary POSIX file I/O for `valid.dat`. It is compiled into `smbtorture` by `source3/torture/wscript_build`.

## Risks and edge cases
- `torture_utable()` performs up to 65,535 remote create/query/delete cycles, so it is slow and sensitive to server throttling.
- `form_name()` returns a static buffer and is not reentrant.
- `torture_casetable()` stores raw host-endian `int` code points in remote file content, so output is a local diagnostic rather than a portable data format.
- Characters such as `.` and `\` are skipped only in `torture_casetable`; other problematic path characters depend on server behavior.
- A fixed `MAX_EQUIVALENCE` of 8 can abort if a server maps too many characters together.

## Test signals
Successful runs print progress and discovered equivalences, create and remove files on the target share, and return `True`. Failures include inability to open the torture connection, create `\utable`, create `valid.dat`, or write the full bitmap.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/utable.c -->
