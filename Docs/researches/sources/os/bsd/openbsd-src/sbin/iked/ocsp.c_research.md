# File Research: sources/os/bsd/openbsd-src/sbin/iked/ocsp.c

Read completely: 621 lines.

Implements asynchronous OCSP certificate validation across iked's privilege-separated processes. The parent process resolves/connects to the OCSP responder and passes a socket fd to the cert process; the unprivileged/cert side builds and sends OCSP requests with OpenSSL, verifies responses, and reports certificate-valid/invalid results back to the IKEv2 process.

State:
- `struct iked_ocsp` tracks the environment, SA header, auth/cert type, responder socket wrapper, OpenSSL BIO, OCSP cert ID, request, and nonblocking request context.
- `struct ocsp_connect` carries the parent-side async connect state: SA header, temporary socket object, responder path, and URL.
- `OCSP_TIMEOUT` is 30 seconds for connect and request I/O callbacks.

Parent/privileged connect path:
- `ocsp_connect()` receives an imsg containing the SA header and optional URL, falls back to `env->sc_ocsp_url`, parses the URL with `OCSP_parse_url()`, rejects OCSP over SSL, opens a nonblocking IPv4 TCP socket, resolves the host, picks the first IPv4 address, and either completes the connect immediately or registers an EV_WRITE timeout callback.
- `ocsp_connect_cb()` handles async connect completion, timeout, and `SO_ERROR`, then calls `ocsp_connect_finish()` with either a valid fd or failure.
- `ocsp_connect_finish()` sends `IMSG_OCSP_FD` to `PROC_CERT`, including the SA header and responder path when fd transfer succeeded; on failure it sends the header with no fd and frees connect state.

Unprivileged/cert validation path:
- `ocsp_validate_cert()` requires an issuer, allocates queue/context records, decodes the DER certificate, creates socket BIO/request/cert-id state, attaches the cert-id to the request, inserts the request into `env->sc_ocsp`, obtains an optional issuer AIA OCSP URL with `X509_get1_ocsp()`, and asks the parent for a connected responder fd.
- `ocsp_free()` closes/frees socket state and OpenSSL BIO/request/context resources.
- `ocsp_receive_fd()` matches the returned SA header to a pending OCSP request, removes it from the pending queue, obtains the passed fd and responder path, binds the fd to the BIO, creates an `OCSP_REQ_CTX`, attaches the request, and registers the nonblocking OpenSSL send/read callback.
- `ocsp_load_certs()` loads PEM X.509 infos from `IKED_OCSP_RESPCERT`, extracts certificates into a stack, and returns `NULL` when no certs were loaded.
- `ocsp_callback()` drives `OCSP_sendreq_nbio()` when the BIO is ready for the requested read/write direction, otherwise rearms the event for the direction OpenSSL wants; timeout fails validation.
- `ocsp_parse_response()` validates response status, loads trusted responder certs, obtains the basic response, checks nonce presence/validity, verifies the response with `OCSP_basic_verify()` (first trusted-other, then default fallback), finds the certificate status for `ocsp_id`, optionally checks this/next update times against configured tolerate/maxage, and treats only `V_OCSP_CERTSTATUS_GOOD` as valid.
- `ocsp_validate_finish()` sends either `IMSG_CERTVALID` or `IMSG_CERTINVALID` with SA header and auth type to `PROC_IKEV2`, then frees OCSP state.

Risks and notes:
- The parent connection path only selects IPv4 results even though `getaddrinfo()` is called with `PF_UNSPEC`.
- OCSP over SSL is explicitly unsupported.
- If no nonce is present in the response, the code logs but does not fail; nonce verification errors do fail.
- The code depends on exact SA-header matching to correlate returned fds with pending OCSP validations.
