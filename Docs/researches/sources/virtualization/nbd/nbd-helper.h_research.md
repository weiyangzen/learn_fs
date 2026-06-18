# File Research: sources/virtualization/nbd/nbd-helper.h

Helper header for transaction logging and readable protocol names.

It defines transaction log control constants, including `NBD_TRACELOG_SET_DATALOG` and `NBD_TRACELOG_FROM_MAGIC`.

It provides inline string conversion helpers for NBD commands, trace log parameter names, and structured reply types. These functions map known constants to their macro names and return `UNKNOWN` for unrecognized values.
