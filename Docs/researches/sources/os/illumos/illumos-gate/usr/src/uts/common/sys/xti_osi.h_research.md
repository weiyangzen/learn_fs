# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/xti_osi.h

`xti_osi.h` defines ISO/OSI-specific XTI option and management constants. Most content is hidden when `_XPG5` is defined, reflecting that these compatibility definitions are for older XTI exposure.

The header defines ISO transport classes `T_CLASS0` through `T_CLASS4`, priority values, protection levels, and the obsolete default TPDU length constant `T_LTPDUDFLT`. Comments state that some options are exposed because XTI specification tests require them, even when the system may not implement the corresponding protocol behavior.

Quality-of-service helper structures model rates and request values: `struct rate` has target and minimum acceptable values; `struct reqvalue` carries called/calling rates; `struct thrpt` combines maximum and average throughput; and `struct transdel` combines maximum and average transit delay.

`ISO_TP` is the protocol level for ISO transport. Connection-oriented option constants cover throughput, transit delay, error/failure probabilities, establishment/release delays, resilience, protection, priority, and expedited data. Connectionless aliases map selected options onto the same values. Management options include TPDU length, acknowledgement/reassignment timers, extended format, flow control, checksum, network expedited data, receipt confirmation, preferred class, and alternate classes.

This header is a standards-compatibility namespace rather than an implementation driver.
