# File Research: sources/virtualization/nvme-cli/plugins/sed/sedopal_cmd.c

SED Opal implementation layer. It uses Linux OPAL ioctls from `linux/sed-opal.h` rather than issuing raw NVMe security commands itself.

Global option state:
- `sedopal_ask_key`
- `sedopal_ask_new_key`
- `sedopal_destructive_revert`
- `sedopal_psid_revert`
- `sedopal_lock_ro`
- `sedopal_discovery_verbose`
- `sedopal_discovery_udev`

Core operations:
- `sedopal_set_key`: either prompts with `getpass` and includes the key in the ioctl payload, or references the kernel keyring when supported.
- `sedopal_cmd_initialize`: checks locking is not already enabled, takes ownership, activates LSP, configures global locking range, and sets password.
- `sedopal_cmd_lock` / `sedopal_cmd_unlock`: call `sedopal_lock_unlock`; unlock rereads partition table with `BLKRRPART`.
- `sedopal_cmd_revert`: supports PSID revert, destructive TPER revert, or preserve-data LSP+TPER revert depending on flags and available ioctl definitions.
- `sedopal_cmd_password`: changes Admin1 password and optionally SID password if `IOC_OPAL_SET_SID_PW` exists.
- `sedopal_cmd_discover`: issues `IOC_OPAL_DISCOVERY`, parses level 0 feature records, prints locking state and optional verbose features.
- `sedopal_locking_state`: returns feature bits from the locking descriptor.

Discovery parsing:
- `sedopal_parse_features` recognizes TPER, locking, geometry, Opal v1/v2, Opalite, Pyrite v1/v2, Ruby, single user mode, datastore, locking LBA, block SID auth, namespace locking, data removal, and namespace geometry.
- Feature printers convert big-endian fields from discovery descriptors and print human-readable capability details.
- `--udev` changes locking output to `DEV_SED_*=` variables suitable for udev rules.

Important safety behavior:
- Destructive and PSID reverts require double interactive confirmation.
- Password length is constrained to 8-32 characters.
- Revert refuses preserve-data operation when the drive is locked.
- Initialization refuses already initialized drives.

Notable issues:
- `sedopal_set_key` compares re-entered password using the first key’s length only; it does not explicitly compare lengths.
- Passwords are copied into ioctl structs and are not scrubbed from memory afterward.
- `sedopal_print_features` defines `sedopal_print_data_removal` but does not call it, so parsed data removal capability is not displayed in verbose output.
