# sources/user-network-fs/samba/source4/librpc/idl/wscript_build

## Purpose

This Waf script generates NDR parser/header/client/Python code from selected source4-specific IDL files.

## Important Targets

The first `SAMBA_PIDL_LIST('PIDL', ...)` handles `ntp_signd.idl`, `opendb.idl`, `sasl_helpers.idl`, `winsif.idl`, and `winsrepl.idl` with `--header --ndr-parser`, outputting to `../gen_ndr`. The second handles `irpc.idl` with `--header --ndr-parser --client --python`, also outputting to `../gen_ndr`.

## Control Flow And State

The script computes `topinclude` from the source tree and passes it as PIDL `--includedir`. It is declarative build metadata and has no runtime behavior.

## Dependencies And Integration Points

It is the build link between the IDL contracts in this folder and generated C/Python artifacts consumed by librpc, IRPC, WINS, NTP signing, SASL helper, and opendb code.

## Risks

Adding an IDL to the wrong PIDL list can omit required client or Python bindings. Incorrect include directory calculation breaks imports such as `nbt.idl` and `server_id.idl`.

## Test Signals

Build tests should ensure generated files appear under `source4/librpc/gen_ndr`, and Python import tests should cover IRPC bindings because only `irpc.idl` requests Python generation.
