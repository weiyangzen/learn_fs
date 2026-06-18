## sources/user-network-fs/libtirpc/src/crypt_client.c

Purpose: Implements `_des_crypt_call`, a client-side RPC wrapper for talking to a local `crypt` service when hardware or external DES support is requested.

Important APIs and control flow: The routine opens a netconfig session, selects the first loopback transport, creates a `CRYPT_PROG`/`CRYPT_VERS` client, populates `desargs` from caller buffer and `desparams`, calls generated `des_crypt_1`, then copies returned encrypted/decrypted data and IV back to the caller for `DESERR_NONE` or `DESERR_NOHWDEVICE`. It frees RPC results and destroys the client.

State and persistence: No cached state; each call opens netconfig and creates a client. External state is the local crypt service and loopback transport database.

Dependencies and integration: Depends on rpcsvc crypt generated interfaces, netconfig iteration, and `clnt_tp_create`. Complements the software DES implementation in `des_crypt.c`/`des_impl.c`.

Risks and test signals: Failing to find loopback or crypt service returns hardware error. Tests should cover no loopback transport, client creation failure, null result, successful data/IV copy, and result freeing.
