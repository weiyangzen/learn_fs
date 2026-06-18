# sources/test-tools/pynfs/nfs4.0/servertests/st_putrootfh.py

Purpose: Minimal conformance test that verifies the server accepts `PUTROOTFH`.

Important APIs/types/functions: Imports constants, `environment.check`, and `nfs_ops.NFS4ops`; exposes one test, `testSupported`.

Control flow: Builds a compound containing only `op.putrootfh()` and checks for success.

State and persistence behavior: Read-only; updates only the current filehandle within the compound to the root filehandle.

Dependencies and integration points: This is a foundational operation used by many other path traversal helpers in the server-test suite.

Risks: Low implementation risk; failures usually indicate fundamental export/root namespace setup problems.

Test signals: A single `check(res)` is the acceptance signal.
