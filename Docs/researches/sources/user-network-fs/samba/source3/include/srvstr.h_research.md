# sources/user-network-fs/samba/source3/include/srvstr.h

## Purpose
`srvstr.h` is a tiny server string helper compatibility header. It maps `srvstr_pull_talloc` to the generic `pull_string_talloc` implementation.

## Important APIs, Types, and Macros
- `srvstr_pull_talloc(ctx, base_ptr, smb_flags2, dest, src, src_len, flags)` expands directly to `pull_string_talloc` with the same arguments.

## Control Flow and State
There is no local control flow or state. The macro preserves a historical server-specific name while deferring all behavior to the generic string conversion routine.

## Persistence Behavior
No persistence is involved.

## Dependencies and Integration Points
Callers must already have `pull_string_talloc` declared and must provide SMB flags and base pointer context appropriate for string decoding. It integrates with SMB request parsing where wire strings are converted into talloc-owned C strings.

## Risks
- As a macro alias, argument side effects are passed through to `pull_string_talloc`.
- Behavior depends entirely on the generic string routine and its interpretation of SMB flags, Unicode state, and buffer bounds.

## Test Signals
SMB1 path/name parsing tests, Unicode/OEM conversion tests, malformed string buffer tests, and compile coverage of legacy callers using `srvstr_pull_talloc`.
