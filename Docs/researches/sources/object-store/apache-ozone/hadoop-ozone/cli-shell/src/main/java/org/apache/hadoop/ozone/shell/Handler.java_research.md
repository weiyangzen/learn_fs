## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/Handler.java

Purpose: base class for Ozone shell commands that open an `OzoneClient` and operate on an `OzoneAddress`.

Important APIs and control flow: implements `Callable<Void>`. `call` loads `OzoneConfiguration`, checks `isApplicable`, obtains an address from `getAddress`, creates a client through `address.createClient(conf)`, invokes subclass `execute`, and closes the client. Utility methods expose security gating, JSON object printing, JSON-array printing with a limit, message output, and the loaded config.

State and dependencies: holds per-invocation `conf`; no persistence. Depends on `AbstractSubcommand`, Ozone client factory via `OzoneAddress`, Jackson JSON helpers, and security utility.

Risks and test signals: subclasses rely on `getAddress` validation before client creation; command-specific failures bubble through `Shell.printError`. No direct test here, but nearly every shell handler uses this lifecycle.
