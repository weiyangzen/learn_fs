# sources/test-tools/pynfs/nfs4.1/client41tests/__init__.py

Purpose: Declares available NFSv4.1 client test modules for package/test discovery.

Important APIs/types/functions: Sets `__all__ = ["ct_reboot.py"]`.

Control flow: No executable control flow beyond module import and assignment.

State and persistence behavior: No persistent state.

Dependencies and integration points: Intended to advertise `ct_reboot.py` to client test discovery, though including the `.py` suffix in `__all__` is unusual for Python module export names.

Risks: Importers expecting module names without extensions may not handle `"ct_reboot.py"` correctly.

Test signals: Package discovery should verify the reboot client tests are found.
