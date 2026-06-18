# sources/test-tools/kdevops/playbooks/python/workflows/dynamic-kconfig/gen-dynamic-pci.py

Purpose: Generates Kconfig entries for PCIe passthrough candidates from `lspci -Dvmmm` output. It enriches labels with sysfs data for NVMe and GPU devices and writes Kconfig directly to stdout.

Key APIs and flow: `main()` validates the input file, scans tagged `Slot`, `SDevice`, `IOMMUGroup`, `Vendor`, and `Device` lines, and calls `add_new_device()` whenever a complete device record ends. `add_new_device()` parses PCI slot topology, assigns sequential config ids, and delegates to `add_pcie_kconfig_entry()`. Device naming goes through `get_kconfig_device_name()`, with helpers for NVMe model/firmware and GPU model/memory display names.

State, dependencies, integration: Reads `/sys/bus/pci/devices`, deletes the input file with `os.unlink()`, and depends only on Python stdlib. It integrates with dynamic-kconfig generation for libvirt PCIe passthrough.

Risks and test signals: It mutates input by deleting it, assumes first NVMe child, catches GPU memory read failures broadly, and `is_gpu_device()` treats regex-like strings as plain substrings. Tests should cover malformed slots, missing IOMMUGroup, NVMe/sysfs absence, GPU naming, quoting, and input deletion expectations.
