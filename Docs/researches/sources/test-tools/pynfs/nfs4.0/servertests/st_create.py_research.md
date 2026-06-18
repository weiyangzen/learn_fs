# sources/test-tools/pynfs/nfs4.0/servertests/st_create.py

## Purpose
`st_create.py` tests the NFSv4 `CREATE` operation for directory, symlink, block/char device, socket, FIFO, invalid parent types, missing filehandle, invalid names, regular-file rejection, read-only/unsupported attributes, and naming policy edge cases.

## Important APIs, Types, And Functions
- `getDefaultAttr(c)` returns default create attributes, currently mode `0o755`.
- `_test_create(t, env, type, name, **keywords)` creates an object of the requested type under the home directory, handles optional support failures, checks OK, then retries and expects `NFS4ERR_EXIST`.
- `_test_notdir(t, env, devpath)` verifies creating under a non-directory returns `NFS4ERR_NOTDIR`.
- `testDir`, `testLink`, `testBlock`, `testChar`, `testSocket`, and `testFIFO` cover supported object types.
- `testDirOff*`, `testNoFh`, `testZeroLength`, `testZeroLengthForLNK`, `testRegularFile`, `testInvalidAttrmask`, `testUnsupportedAttributes`, `testDots`, `testSlash`, and `testLongName` cover negative and edge behavior.

## Control Flow
Most type tests delegate to `_test_create`, which builds a `createtype4`, issues a `go_home()` compound plus `CREATE`, and repeats the same compound for existence validation. Negative tests use `c.create_obj` on composed paths or raw compounds without current filehandle. Unsupported-attribute tests compute unsupported writable attrs from `env.attr_info` and the server's `supportedAttrs`.

## State And Persistence Behavior
Tests create objects under the test export and rely on repeated CREATE observing existing names. They mutate directory entries and may leave objects for environment cleanup. No local persistent state is maintained.

## Dependencies And Integration Points
The module imports NFS constants, `createtype4`, `specdata4`, `check`, and `nfs_ops`. It depends on environment home directory paths, long name bytes, attribute metadata, and client helpers.

## Risks And Edge Cases
- `_test_create` passes `t.word()` as the created name instead of the `name` label, so repeated calls depend on `t.word()` stability within a test.
- Some tests accept multiple statuses or warn for optional behavior, such as allowing `"."`/`".."`
  or slash-containing names.
- `testZeroLengthForLNK` has a message mentioning zero-length name while the code uses zero-length symlink data and generated object name; expected statuses include `NFS4ERR_NOENT`.
- The nested `testNamingPolicy` is indented under a non-test block and likely not discovered.

## Test Signals
Signals include OK object creation, `NFS4ERR_EXIST` on duplicate names, `NFS4ERR_NOTDIR`/`NFS4ERR_SYMLINK` under invalid parents, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_INVAL`, `NFS4ERR_BADTYPE`, `NFS4ERR_ATTRNOTSUPP`, `NFS4ERR_BADNAME`/`BADCHAR`, and `NFS4ERR_NAMETOOLONG`.
