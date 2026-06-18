# sources/test-tools/fio/fio.c

Purpose: command-line fio entry point. It initializes global fio state, parses arguments, starts either remote-client orchestration or local backend execution, and performs final key/global cleanup.

Important APIs/types/functions: the only function is `main(int argc, char *argv[], char *envp[])`. It calls `initialize_fio`, `fio_server_create_sk_key`, `parse_options`, `fio_time_init`, `set_genesis_time`, `fio_start_all_clients`, `fio_handle_clients`, `fio_backend`, `fio_server_destroy_sk_key`, and `deinitialize_fio`.

Control flow: startup returns immediately on failed `initialize_fio`. It creates the server shared-key material before option parsing, then parses CLI/job options. Standard output is switched to line buffering so multi-threaded status output is less interleaved. After time initialization, `nr_clients` selects remote-client mode: set genesis time, start all clients, and handle client callbacks through `fio_client_ops`. With no clients, it runs the normal backend with no socket-output object. Both success and failure paths destroy the server key before deinitializing fio.

State and persistence behavior: persistent external effects are whatever option parsing and backend/client execution perform; this file itself only mutates process-global initialization state, stdout buffering, timing baseline, and server-key lifecycle. Return value starts as failure and is overwritten by client/backend execution result.

Dependencies/integration: includes `fio.h`, so it relies on the full fio core. It is the top-level integration point among initialization, option parsing, time setup, network client mode, and local job execution.

Risks and test signals: cleanup labels must preserve `fio_server_destroy_sk_key` when key creation succeeded and `deinitialize_fio` for all initialized exits. Tests should cover option-parse failure, key-create failure, local backend success/failure, client mode with failed `fio_start_all_clients`, and line-buffered output behavior under multiple jobs.
