# sources/test-tools/stress-ng/stress-pci.c

Purpose: `stress-pci.c` implements the Linux `pci` stressor, scanning PCI sysfs device directories and repeatedly opening, mmaping, and reading regular PCI attribute/resource files.

Important APIs/types/functions: `stress_pci_info_t` stores sysfs path, device name, ignore flag, per-device read metrics, and list linkage. Discovery uses `stress_pci_dev_filter()`, `stress_pci_info_get_by_name()`, and `stress_pci_info_get()`, with optional `--pci-dev`. `stress_pci_exercise_file()` opens a sysfs file, validates it is regular/nonempty, tries `mmap`, reads non-ROM files, and toggles ROM access. `stress_pci_handler()` longjmps out of unexpected SIGSEGV/SIGBUS.

Control flow: the stressor resolves optional operation rate, synchronizes, installs SIGSEGV/SIGBUS handlers, builds a linked list from `/sys/bus/pci/devices`, and loops over unignored devices. Each device directory is scanned, files are exercised, bogo ops increment, and optional rate limiting sleeps until the next target time. If a signal occurs while reading/mmaping a device, that device is marked ignored and iteration continues.

State and persistence behavior: state is the heap device list plus per-device metric counters. Sysfs files are opened read-only except ROM files, where `"1\n"` and `"0\n"` are written to enable/disable ROM access. No normal filesystem persistence is created.

Dependencies and integration points: Linux sysfs PCI layout, `scandir`, `mmap`, `read`, signal longjmp, stress-ng settings, metrics, rate limiting, sync barriers, and `CLASS_OS` registration.

Risks: PCI sysfs contents vary by hardware, permissions, driver state, and platform firmware. Reading or mmaping resource/ROM files can trigger SIGBUS/SIGSEGV or hardware-specific failures, so signal recovery and ignore flags are important. ROM reads are deliberately avoided because reported ROM sizes can be unreliable.

Test signals: `--pci` should skip when no sysfs entries exist and otherwise report config/resource MB/s for instance zero. `--pci-dev` should limit discovery to one device. Tests should cover permission-denied resource files, signal recovery, rate limiting, and cleanup of allocated device lists.
