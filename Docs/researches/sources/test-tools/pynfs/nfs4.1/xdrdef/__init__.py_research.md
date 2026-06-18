# sources/test-tools/pynfs/nfs4.1/xdrdef/__init__.py

Purpose: empty package marker for generated NFSv4.1 XDR modules.

Important APIs/types/functions: none; the file has zero lines.

Control flow: no runtime behavior.

State and persistence behavior: no state beyond making `xdrdef` importable as a package.

Dependencies/integration: sibling generated modules such as `nfs4_const`, `nfs4_type`, and `nfs4_pack` are imported throughout server tests.

Risks and test signals: absence of package initialization is intentional. Any needed generated module availability is handled by build/setup rather than this file.
