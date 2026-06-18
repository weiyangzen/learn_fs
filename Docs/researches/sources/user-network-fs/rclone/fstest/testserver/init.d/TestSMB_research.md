
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMB

Purpose: starts a Samba container for SMB backend integration tests.

Important APIs/types/functions: uses `dperson/samba`, maps local port `28630` to SMB 445 TCP/UDP, creates user `rclone`, workgroup `thepub`, read-only `public` share, and writable `rclone` share.

Control flow: Docker run, then config emission with host, port, credentials, domain, and `_connect`.

State/persistence: disposable container shares.

Dependencies/integration: Docker lifecycle and rclone SMB backend tests.

Risks: SMB on nonstandard local port depends on backend support. Fixed credentials and guest share are test-only.

Test signals: connect to local SMB port and successful operations on share `rclone`.
