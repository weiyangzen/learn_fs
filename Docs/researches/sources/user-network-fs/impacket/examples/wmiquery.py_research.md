# sources/user-network-fs/impacket/examples/wmiquery.py

Purpose: `wmiquery.py` is an interactive and batch WQL client for Windows Management Instrumentation over DCOM. It executes arbitrary WQL queries, prints tabular result properties, and describes WMI classes through `GetObject()`.

Important APIs, types, and functions: The `WMIQUERY` command class is defined inside the `__main__` block. It implements `do_describe()`, `default()` for WQL query execution, `printReply()` for enumerator output, `do_lcd()`, local shell execution via `do_shell()`, and `do_exit()`. The CLI establishes `DCOMConnection`, obtains `IWbemLevel1Login`, logs into a configurable namespace, and optionally adjusts RPC auth level to packet integrity or privacy.

Control flow: The CLI parses credentials, namespace, optional command file, COM version, and auth-level controls. It prompts for a password when necessary, splits hashes, connects to DCOM with Kerberos or NTLM, obtains WMI services, and releases the login interface. Without `-file`, it enters a WQL prompt. With `-file`, it echoes each command and executes it through `onecmd()`. Query results are consumed by repeated `iEnum.Next()` calls until an exception containing `S_FALSE` marks enumeration completion.

State and persistence behavior: Persistent remote state is not intentionally modified by this script; it is query/describe focused. Local state is the command shell, current local directory if `lcd` is used, and optional batch file handle. The `!` command can execute arbitrary local shell commands, so local side effects are possible.

Dependencies and integration points: The script uses Impacket DCOM/WMI wrappers, RPC auth constants, `parse_target()`, and the example logger. It integrates with any WMI namespace that the credentials can access; some namespaces may require `-rpc-auth-level privacy`.

Risks: Arbitrary WQL execution can be expensive or reveal sensitive host data. `do_describe()` indexes `sClass[-1:]` safely for empty strings but still sends empty class names to WMI if the user enters blank describe input. `printReply()` uses exception string matching for `S_FALSE`, which is brittle. Local `!` commands are intentionally powerful and can affect the operator machine. Query output assumes property values are printable and may be noisy for large result sets.

Test signals: Mock tests can exercise WQL trimming, semicolon removal, table printing for scalar and list values, batch file command dispatch, RPC auth-level selection, and cleanup on connection errors. Integration tests require a WMI endpoint or recorded COM enumerator fixtures.
