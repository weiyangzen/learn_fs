# sources/user-network-fs/samba/source4/torture/smb2/deny.c

## Purpose

`deny.c` implements the SMB2 deny/share-mode matrix tests. It opens the same file through one or two SMB2 tree connections with many combinations of desired access and share access, then verifies whether the second open can read, write, both, neither, or cannot open. It registers the `deny` suite with single-connection and two-connection variants.

## Important APIs, Types, and Functions

- `enum deny_result` encodes expected behavior: `A_X` for first-open failure, `A_0` for no read/write access by the second handle, `A_R`, `A_W`, and `A_RW`.
- `denytable[]` is the central expectation table. Each row includes whether the target is `.exe` or `.dat`, first desired access/share access, second desired access/share access, and expected outcome.
- Formatting helpers `denystr()`, `openstr()`, and `resultstr()` turn table values into readable torture output.
- `torture_smb2_denytest2()` runs the two-tree matrix; `torture_smb2_denytest1()` calls it with the same tree for both arguments.
- SMB2 operations used are `smb2_create`, `smb2_read`, `smb2_write`, `smb2_util_write`, `smb2_util_close`, and `smb2_util_unlink`.

## Control Flow

The test creates two seed files, `denytest2.dat` and `denytest2.exe`, writes a small payload into each, and then iterates over every row in `denytable`. For each row it opens the target file once with `mode1` and `deny1`, then attempts a second open with `mode2` and `deny2`. If the first open fails, the result is `A_X`; if the second open fails, the result is `A_0`; otherwise the test attempts a one-byte read and one-byte write through the second handle and combines successful operations into `A_R`, `A_W`, or `A_RW`.

The observed result is compared against the row's expected `deny_result`. If `showall` is enabled, or when a mismatch occurs, the test prints elapsed time, filename, share modes, access modes, observed result, and expected result. It closes both handles after each row and unlinks the seed files during cleanup.

## State and Persistence Behavior

Persistent state is limited to two temporary files with known names and one-byte/short-string content. The deny matrix mutates file content when rows allow writes through the second handle, but the test only needs read/write success status, not stable content. Handles are opened and closed for each row to avoid carrying share-mode state between combinations.

The expectation table is static and source-controlled. It acts as the persistent specification for Windows-compatible SMB2 share-mode behavior across executable and non-executable names.

## Dependencies and Integration Points

The source depends on SMB2 client calls and the torture SMB2 registration helpers. `torture_smb2_deny_init()` registers `deny1` via `torture_suite_add_1smb2_test()` and `deny2` via `torture_suite_add_2smb2_test()`, integrating with the harness's ability to provide one or two tree connections.

The test is an integration point for server share-mode enforcement, desired-access mapping, executable-file special cases, same-connection versus cross-connection behavior, and read/write I/O authorization after opens have succeeded.

## Risks and Edge Cases

- The large static table is hard to audit manually; table drift or a single mistaken row can create broad compatibility noise.
- The same filenames are used for every run, so parallel runs in one share namespace can interfere.
- Some rows write through the second handle; if a server's share-mode behavior depends on file content or oplocks outside this test, failures may be hard to diagnose from the matrix alone.
- Progress output is enabled by default through the `progress` setting and uses carriage returns, which can be noisy in non-interactive logs.
- The expected behavior distinguishes `.exe` and `.dat`, so filesystems or servers without executable-name-specific handling may intentionally differ.

## Test Signals

Pass signals are successful seed-file creation, completion of every `denytable` row without mismatches, exact read/write/open result classification per row, and successful cleanup. Failure output includes the mismatched row's share/access modes and observed versus expected symbolic result, making this suite useful for pinpointing share-mode regressions.
