# sources/distributed-fs/xrootd/src/XrdCl/XrdClTls.cc

## Purpose

This file implements the XrdCl TLS wrapper over `XrdTlsSocket`. It initializes a process-wide TLS context, configures TLS logging, performs nonblocking TLS handshakes with host verification, maps TLS read/write retry states into XrdCl statuses, and remaps poll events during handshake reversals.

## Important APIs, Types, and Functions

`InitTLS` creates the global `XrdTlsContext` once, using `X509_CERT_DIR`/`X509_CERT_FILE` or `/etc/grid-security/certificates`, validates CA directory permissions, and records `NoTlsOK` on failure. `SetTlsMsgCB` installs XrdTls message/debug callbacks based on `TlsDbgLvl`. `Tls::Connect`, `Read`, `ReadV`, `Send`, `Shutdown`, `ToStatus`, `MapEvent`, and `ClearErrorQueue` implement the wrapper.

## Control Flow

The constructor installs callbacks, calls `InitTLS`, throws on failure, and creates a nonblocking handshake socket wrapper. `Connect` skips host verification for loopback names, calls TLS connect, logs and returns errors, uncorks the underlying socket when the handshake needs I/O, and enables or disables uplink depending on whether TLS wants write or read. `Read` and `Send` call TLS I/O, convert status, manage handshake reversal states (`ReadOnWrite`, `WriteOnRead`), alter uplink notifications, and return `suRetry` when no bytes moved. `ReadV` emulates vector reads by sequential TLS reads.

## State and Persistence Behavior

TLS context is a process-global `unique_ptr` guarded by a static mutex. Per-socket state includes the underlying `Socket`, owned `XrdTlsSocket`, handshake reversal state, and socket handler pointer. No on-disk state is written, but environment variables and `DefaultEnv` affect initialization.

## Dependencies and Integration Points

It depends on `XrdTls`, `XrdTlsContext`, `XrdTlsSocket`, XrdCl socket/poller/default environment/logging, `XrdOucUtils::ValPath`, and async socket handlers for uplink toggles. `Socket::TlsHandShake` and encrypted streams use it.

## Risks and Edge Cases

Once initialization fails, `NoTlsOK` can suppress later attempts even if environment changes. CA path validation may reject deployments with unusual permissions. TLS wants-read/wants-write reversal must stay synchronized with poller event mapping or handshakes can stall. `TLS_SSL_Error` maps to fatal `errTlsError` with `EAGAIN`, which can be confusing diagnostically.

## Test Signals

Tests should cover successful context initialization, missing/invalid CA paths, loopback verification bypass, want-read/write handshake transitions, event remapping, zero-byte retry behavior, TLS close mapping to socket error, and debug callback setup.
