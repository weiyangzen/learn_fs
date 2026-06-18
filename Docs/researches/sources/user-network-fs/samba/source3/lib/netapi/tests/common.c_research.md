# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/common.c

Purpose: shared command-line option implementation for the libnetapi example/test programs. It maps common popt options into the process-global/current libnetapi context.

Important APIs/functions: `popt_common_callback` handles `--user/-U`, `--password/-p`, `--debuglevel/-d`, and `--kerberos/-k`. `popt_common_netapi_examples` defines the shared popt table included by test binaries through `POPT_COMMON_LIBNETAPI_EXAMPLES`.

Control flow: the callback calls `libnetapi_getctx`, ignores pre/post callback phases, and switches on option value. For `-U user%password`, it splits a temporary copy, sets username/password, then overwrites the password portion of the original argument with `X` characters. For `-U user`, it only sets username; password and Kerberos options use dedicated setters.

State and persistence: mutates the current `libnetapi_ctx` credentials, debug level, and Kerberos mode. It also mutates the command-line argument buffer to mask an inline password. No persistent files are written.

Dependencies/integration: depends on popt, public `netapi.h`, and `common.h`. Every test binary can include the common option table so tests share credential/debug behavior.

Risks: overwriting `arg` requires casting away constness through pointer gymnastics; this assumes popt's argument storage is writable. Inline passwords still exist briefly in process memory and shell history before masking. The callback assumes a libnetapi context already exists; test programs must call `libnetapi_init` before option parsing.

Test signals: tests should parse `-U user`, `-U user%pass`, `-p pass`, `-d level`, and `-k`, then verify the context reflects them. A robustness test should run against readonly argv storage if the platform permits, because the masking behavior is nonportable.
