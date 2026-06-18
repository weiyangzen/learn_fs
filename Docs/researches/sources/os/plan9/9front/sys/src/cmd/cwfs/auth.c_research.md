# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/auth.c

Factotum-backed authentication support and config-device stubs.

Important behavior:
- `nvrgetconfig()` returns `conf.confdev`; `nvrsetconfig()` is a no-op success stub here.
- `authnew()` mounts `/srv/factotum` if needed, opens `/mnt/factotum/rpc`, allocates an `AuthRpc`, and starts `proto=p9any role=server`.
- `authread()` advances the auth protocol, returns challenge bytes, and on `ARdone` records the authenticated user id in the `File`.
- `authwrite()` feeds client data into factotum.
- Errors are reported through the channel’s error buffer.
