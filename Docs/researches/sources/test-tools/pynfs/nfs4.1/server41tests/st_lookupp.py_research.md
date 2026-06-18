# sources/test-tools/pynfs/nfs4.1/server41tests/st_lookupp.py

Purpose: validates `LOOKUPP` parent-directory traversal and error handling for invalid current filehandle types.

Important APIs/types/functions: `testLookupp`, object-type tests `testFile`, `testFifo`, `testLink`, `testBlock`, `testChar`, `testSock`, plus `testLookuppRoot`, `testNoFH`, and `testXdev`.

Control flow: `testLookupp` walks down `env.home`, records filehandles with `GETFH`, then repeatedly issues `LOOKUPP` and compares returned handles to the earlier path handles. Object-type tests put a known non-directory filehandle as current fh and expect `NOTDIR` or `SYMLINK`. Root and missing-fh tests validate `NOENT` and `NOFILEHANDLE`; the xdev case checks parent traversal across a configured special path returns the expected parent filehandle.

State and persistence behavior: no new durable objects are created. The tests depend on prebuilt test-tree objects and the server's filehandle stability across lookup and lookupp operations.

Dependencies/integration: uses `use_obj` environment helper, `NFS4ops`, and option paths such as `usefile`, `usefifo`, `usesocket`, and `usespecial`.

Risks and test signals: most tests require `--maketree` or equivalent configured objects. Filehandle byte equality is the key signal; cross-filesystem semantics may vary for `testXdev`.
