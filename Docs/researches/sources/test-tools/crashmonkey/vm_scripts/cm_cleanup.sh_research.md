# sources/test-tools/crashmonkey/vm_scripts/cm_cleanup.sh

Purpose: cleanup helper for CrashMonkey kernel modules and mount state inside a VM or host.

Important APIs/types/functions: `umount /mnt/snapshot`, `rmmod disk_wrapper.ko`, and `rmmod cow_brd.ko`. Control flow is linear with no argument validation.

State/persistence behavior: unmounts the snapshot mount and unloads kernel modules, affecting the running system. Dependencies/integration: called by remote trigger scripts and `xfsMonkey.py` equivalent cleanup.

Risks/test signals: ignores errors, assumes module names/paths, and may fail if busy or if modules are named without `.ko` after insertion.
