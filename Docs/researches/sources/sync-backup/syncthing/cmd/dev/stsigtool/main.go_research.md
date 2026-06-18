# sources/sync-backup/syncthing/cmd/dev/stsigtool/main.go

Purpose: development/release utility for generating signing keys, signing data, and verifying Syncthing upgrade signatures.

Important APIs/types/functions: commands `gen`, `sign <privkeyfile> [datafile]`, and `verify <signaturefile> <datafile> [pubkeyfile]`; functions `gen`, `sign`, `verifyWithFile`, and `verifyWithKey`. It uses `lib/signature` and the built-in `upgrade.SigningKey`.

Control flow: command dispatch is based on first argument. `gen` writes private then public key bytes to stdout. `sign` reads a private key, reads data from file or stdin, signs, and writes signature to stdout. `verify` reads signature and data, using either supplied public key or built-in upgrade key, and logs success.

State and persistence behavior: reads key/data files and writes binary output to stdout; no durable files unless shell redirection is used.

Dependencies/integration: used by release workflow to sign archives and by upgrade verification logic through shared signature APIs.

Risks/test signals: usage text does not exit early, so missing args can fall through without an explicit error for unknown command. Binary stdout must be redirected carefully. Signal is successful signature verification or fatal error.
