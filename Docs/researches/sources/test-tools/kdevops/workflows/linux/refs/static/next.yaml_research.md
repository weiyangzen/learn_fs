## sources/test-tools/kdevops/workflows/linux/refs/static/next.yaml

Purpose: Static ref manifest for linux-next and fs-next/current branches.

Important APIs/types/functions: Entries include `master`, dated `next-20250328`, `fs-current`, and `fs-next`, mapped to `BOOTLINUX_TREE_NEXT_REF_*` symbols.

Control flow: Data-only selection set.

State and persistence: Static YAML metadata.

Dependencies and integration points: Integrated into `Kconfig.next` and bootlinux default/ref logic.

Risks and test signals: Dated next refs can age out of relevance, while `master` moves continuously. Test clone checkout and kernel config presence.
