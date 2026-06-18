# sources/user-network-fs/samba/source4/torture/libnetapi/libnetapi.c

## Purpose
This file initializes libnetapi torture support and registers the `netapi` smbtorture suite.

## Important APIs, types, and functions
`torture_libnetapi_init_context()` loads the torture smb.conf, loads interfaces, retrieves command-line credentials, and calls `libnetapi_net_init`. `torture_libnetapi_initialize()` checks that `libnetapi_init()` succeeds when a context is already set up. `torture_libnetapi_init()` registers server, group, user, and initialize tests.

## Control flow
Context initialization first forces `lp_load_global()` using the test config path, then creates a source3 libnetapi context bound to the source4 torture loadparm context and credentials. Suite initialization builds a `torture_suite`, adds simple tests, sets a description, and registers it.

## State and persistence behavior
The file mainly manages in-memory context state. It may affect process-global configuration by loading smb.conf and interfaces. It does not directly mutate remote server state.

## Dependencies and integration points
It bridges source4 `smbtorture` to source3 `libnetapi`, `netapi_private`, command-line credentials, and global loadparm/interface initialization. Other libnetapi test files depend on `torture_libnetapi_init_context()`.

## Risks and edge cases
Incorrect config loading can cause all NetAPI tests to fail before network calls. The function's return type is `bool` but returns `W_ERROR_V(WERR_GEN_FAILURE)` on one failure path, which works as truthiness only if interpreted carefully.

## Test signals
The initialize test confirms that pre-initialized libnetapi contexts can be passed through `libnetapi_init` without losing the context, and suite registration exposes all NetAPI subtests under `smbtorture`.
