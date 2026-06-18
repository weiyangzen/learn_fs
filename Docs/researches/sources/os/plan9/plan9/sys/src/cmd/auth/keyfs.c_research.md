# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/keyfs.c

Implements a standalone 9P filesystem serving encrypted account key databases, mounted by default at `/mnt/keys`. It exposes users as directories with files `key`, `secret`, `log`, `status`, `expire`, and `warnings`.

The server reads/writes `/adm/keys`-style fixed-record databases encrypted with old DES CBC using an auth key from nvram or an entered password. It supports creating/removing/renaming user directories, reading and writing DES keys/secrets, recording bad/good login counts, purgatory delays after repeated failures, expiration, disabled status, and warning counters.

The 9P server is handwritten around `Fcall`, fid tracking, qids, and `convM2S`/`convS2M`. It reloads the key file when mtime changes and can periodically exec `auth/warning`. User records use fixed `ANAMELEN` names and hash buckets.
