# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_userconf.c

Implements OpenBSD’s interactive User Kernel Config shell, used early in boot to inspect and modify kernel autoconfiguration tables before normal device attachment. It edits `cfdata`, pseudo-device counts, locator values, flags, and device enabled/disabled states.

Global state tracks number base, max/total device slots, locator-name count, pagination, command history, command buffers, and external config arrays such as `cfdata`, `locnames`, `locnamp`, `cfroots`, `pv`, `pdevnames`, and `pdevinit`.

`userconf_init()` scans `cfdata` to find active and free slots and determines the highest locator name index. Display helpers print numbers in selected base, print device names/states, print full device records including parents, locators, flags, and pseudo-device counts, and paginate output with `userconf_more()`.

Parsing helpers include `userconf_number()` for signed decimal/octal/hex input, `userconf_device()` for device tokens like `sd0` or `sd*`, and `userconf_attr()` for locator attribute names. History helpers append compact command records for later replay or visibility.

Mutation commands include `userconf_change()` for changing locators/flags or pseudo-device counts, `userconf_disable()` and `userconf_enable()` for real devices and pseudo devices, and `userconf_add()` for cloning a device entry into a free `cfdata` slot. Adding shifts `cfdata`, fixes parent-vector and root indices, updates max device count, and adjusts star-unit handling for wildcard entries.

Query commands include `userconf_help()`, `userconf_list()`, `userconf_show()`, `userconf_show_attr()`, `userconf_common_attr_val()`, and `userconf_common_dev()`. These support listing all devices, attributes, matching devices by locator value, and finding devices by name/unit/wildcard.

`userconf_parse()` dispatches commands and aliases: add, base, change, optional ddb, disable, enable, exit/quit, find, help, list, lines, show, verbose, and `?`. `user_config()` enters console polling mode, runs the `UKC>` prompt until quit, then resumes boot.

Filesystem relevance: primarily device-autoconfiguration rather than filesystem logic. It can enable/disable/change storage controller and block-device configuration before VFS mounts root, so it can indirectly determine which filesystem devices exist at boot.
