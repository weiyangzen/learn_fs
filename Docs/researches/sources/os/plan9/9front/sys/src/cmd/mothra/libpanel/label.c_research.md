# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/label.c

Implements passive text/bitmap labels.

Key behavior:
- Stores icon/text plus placement.
- Draws inside a passive box.
- Computes size from icon/text size.
- Provides `plplacelabel()` to change placement.

Important dependencies: `pl_drawicon`, `pl_iconsize`, `pl_box`.

Notable risks:
- Label icon/text pointer is borrowed; lifetime is caller-managed.
