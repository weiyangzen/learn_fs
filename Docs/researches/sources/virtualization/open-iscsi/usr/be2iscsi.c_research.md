# File Research: sources/virtualization/open-iscsi/usr/be2iscsi.c

Contains transport-specific connection setup limits for the `be2iscsi` offload driver. `be2iscsi_create_conn` clamps:
- receive data segment length to 65536,
- first burst to 8192,
- max burst to 262144,
- transmit data segment length to 65536.

It also forces `ERL=0` and `InitialR2T=1`. This adapts generic session/connection settings to firmware or hardware constraints before login/connection use.
