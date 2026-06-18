# File Research: sources/virtualization/open-iscsi/usr/cxgbi.c

Contains the Chelsio `cxgb3i/cxgb4i` transport helper. `cxgbi_create_conn` limits `conn->max_recv_dlength` to 8192, despite a comment noting the card can handle up to 15360 bytes. This is a narrow hardware compatibility adjustment.
