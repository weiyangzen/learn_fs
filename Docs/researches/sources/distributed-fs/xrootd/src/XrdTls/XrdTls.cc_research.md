# sources/distributed-fs/xrootd/src/XrdTls/XrdTls.cc

Purpose: Implements common TLS diagnostics, debug control, and OpenSSL error-code conversion for the XrdTls facade.

Important APIs/types/functions: XrdTls::Emsg() routes optional messages through a global callback and can flush the OpenSSL error queue via ERR_print_errors_cb(). XrdTls::RC2Text() maps XrdTls::RC values to user-facing reason strings. SetDebug() overloads connect XrdTlsGlobal::SysTrace to either an XrdSysLogger or callback. SetMsgCB() installs the global message callback. ssl2RC(), ssl2Text(), and ClearErrorQueue() translate or clear OpenSSL state.

Control flow: Default messages go to stderr through ToStdErr(). Emsg() normalizes a null trace id to TLS, emits msg if present, optionally mirrors to stderr when dbgOUT/echoMsg is active, then prints pending OpenSSL errors if flush is true. ssl_msg_CB() is the ERR_print_errors_cb adapter.

State/persistence: Global process state includes XrdTlsGlobal::SysTrace, msgCB, and echoMsg. There is no durable persistence.

Dependencies/integration: Used by XrdTlsContext and XrdTlsSocket for all error reporting and by TLS trace macros through XrdTlsGlobal::SysTrace. Depends on OpenSSL ERR/SSL and XrdSysE2T.

Risks: Global callbacks are not protected by locks here, so applications should set them during initialization as documented. Emsg() only clears OpenSSL errors when flush is true; callers that pass false must ensure the queue is otherwise handled.

Test signals: Verify RC2Text/ssl2RC/ssl2Text mappings, callback routing, dbgOUT mirroring, and OpenSSL error queue flushing in failure paths from context and socket code.
