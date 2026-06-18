# sources/user-network-fs/impacket/examples/wmipersist.py

Purpose: `wmipersist.py` installs or removes a permanent WMI event consumer, event filter, timer instruction, and filter-to-consumer binding in `root/subscription`. The installed consumer executes supplied VBScript when a WQL event filter or interval timer fires.

Important APIs, types, and functions: `WMIPERSISTENCE` stores credentials, NTLM hashes, and CLI options. `checkError()` reads the WMI call status, maps known `WBEMSTATUS` values, and logs success or failure. `run()` creates the DCOM/WMI connection, logs into `//./root/subscription`, and branches on `INSTALL` versus `REMOVE`. Install mode spawns `ActiveScriptEventConsumer`, `__EventFilter`, optional `__IntervalTimerInstruction`, and `__FilterToConsumerBinding` instances. Remove mode deletes those instances by constructed WMI object paths.

Control flow: The CLI validates COM version, install action requirements, and mutually exclusive `-filter`/`-timer`. It parses target credentials, prompts for a password when needed, enables Kerberos when `-aesKey` is supplied, instantiates `WMIPERSISTENCE`, and calls `run()`. Install mode reads the entire VBS file, creates the consumer with `ScriptingEngine='VBScript'`, builds either a caller-provided WQL filter in `root\\cimv2` or a timer-backed filter in `root\\subscription`, and links the filter to the consumer. Remove mode attempts to delete all related objects for the name, including timer objects even if the original install was filter-based.

State and persistence behavior: The important state is remote and persistent: WMI subscription objects remain on the target until removed and can keep executing the script after the tool exits. Local state is limited to credentials and the opened VBS file. DCOM is disconnected after object creation/removal.

Dependencies and integration points: The script uses Impacket DCOM/WMI wrappers, `COMVERSION`, `parse_target()`, the example logger, and WMI class/object path semantics. It integrates with Windows WMI permanent eventing infrastructure and relies on administrative permissions in `root/subscription`.

Risks: This is explicitly persistence-oriented functionality; installed consumers may execute repeatedly and invisibly based on event or timer triggers. Names and WQL filters are interpolated into WMI paths and queries, so malformed names can break cleanup. The implementation references the global `options` variable inside `run()` instead of consistently using `self.__options`, reducing reusability. CreatorSID is hard-coded. Remove mode logs individual failures but does not roll back partial deletes.

Test signals: Tests should mock WMI service objects and verify install object fields, timer versus filter branching, binding paths, remove paths, and `checkError()` status mapping. CLI tests should cover mutual exclusion of `-filter` and `-timer`, password prompting conditions, COM version validation, and Kerberos enabling with AES keys.
