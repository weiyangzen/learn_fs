# sources/user-network-fs/samba/source3/smbd/smb2_keepalive.c

Purpose: implements the SMB2 keepalive/echo-style command with a minimal success response.

Important API: `smbd_smb2_request_process_keepalive()` verifies body size `0x04`, allocates a `0x04` response body, writes structure size and reserved fields, and completes the request.

Control flow: invalid body size returns an SMB2 error. Response allocation failure returns `NO_MEMORY`. Success calls `smbd_smb2_request_done()` with no dynamic output. A TODO notes that timestamp updates may be added later.

State and persistence: no explicit state changes today.

Dependencies and integration: depends on SMB2 request size verification, response body allocation, and request completion helpers. It integrates as a lightweight liveness command in SMB2 dispatch.

Risks: protocol conformance is simple but future timestamp updates could affect idle timeout semantics.

Test signals: cover successful keepalive, malformed body size, allocation failure path if injectable, and behavior under signed/encrypted/session-active states.
