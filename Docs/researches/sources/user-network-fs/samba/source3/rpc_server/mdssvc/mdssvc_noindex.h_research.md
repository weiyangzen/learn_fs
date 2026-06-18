# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_noindex.h

Purpose: exposes the noindex backend vtable to the mdssvc core.

Important API: declares `extern struct mdssvc_backend mdsscv_backend_noindex;`, which is selected by `mds_init_ctx()` and initialized/shutdown by the process-level mdssvc setup.

Control flow and integration: this header lets `mdssvc.c` compile the fallback backend unconditionally. The backend implements enough callbacks to satisfy normal query lifecycle without external services.

State and persistence: no declarations introduce additional state; all state is managed by the common mdssvc structures.

Dependencies: relies on `struct mdssvc_backend` from `mdssvc.h` being visible before use.

Risks: the include guard close comment says `_MDSSVC_VOID_H_`, which is cosmetic but misleading. API surface is intentionally tiny.

Test signals: build coverage is sufficient for the header; behavior is tested via the C backend and mdssvc core.
