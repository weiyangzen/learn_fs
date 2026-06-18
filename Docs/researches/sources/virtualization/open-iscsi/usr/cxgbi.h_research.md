# File Research: sources/virtualization/open-iscsi/usr/cxgbi.h

Declares `cxgbi_create_conn(struct iscsi_conn *)` behind a simple include guard. It forward declares `struct iscsi_conn` and leaves all transport details to `cxgbi.c`.
