# sources/test-tools/pynfs/nfs4.1/MANIFEST.in

Purpose: Source distribution manifest rules for NFSv4.1 pynfs XDR files.

Important APIs/types/functions: This is a packaging data file, not Python code. It includes `*.x` files and excludes generated `*_const.py`, `*_pack.py`, and `*_type.py` files.

Control flow: Interpreted by setuptools/distutils during source distribution creation.

State and persistence behavior: Does not mutate runtime state; controls which files appear in built sdists.

Dependencies and integration points: Integrates with the XDR generation workflow where generated Python files can be recreated from checked-in `.x` specifications.

Risks: If generated files are needed at install time but generation is unavailable, excluding them can break consumers. Conversely, including only `.x` avoids stale generated code in source archives.

Test signals: Packaging validation should confirm `.x` files are present in sdists and generated files are absent.
