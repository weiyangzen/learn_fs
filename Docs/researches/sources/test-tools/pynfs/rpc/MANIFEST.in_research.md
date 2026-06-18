# sources/test-tools/pynfs/rpc/MANIFEST.in

Purpose: packaging manifest rules for the pynfs RPC package XDR sources and generated artifacts.

Important APIs/types/functions: includes `*.x`; excludes `*_const.py`, `*_pack.py`, and `*_type.py`.

Control flow: declarative packaging metadata only.

State and persistence behavior: affects source distributions by keeping XDR inputs and excluding generated Python outputs.

Dependencies/integration: complements the XDR generation flow used by setup/build tooling.

Risks and test signals: packaging must regenerate excluded files at build time; missing generator integration would produce incomplete installs.
