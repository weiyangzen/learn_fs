# sources/test-tools/pynfs/nfs4.1/errorparser.py

## Purpose
`errorparser.py` reads XML descriptions of proxy fault-injection scenarios and applies them to NFSv4 operations. It supports per-operation matching, random frequency, optional delay, injected status codes, and argument-mutation functions defined in `errorfunctions.py`.

## Important APIs, Types, And Functions
- `ErrorDesc` stores lists for `name`, `operation`, `errorcode`, `function`, `delay`, and `frequency`, with defaults of no delay and one-in-ten frequency.
- `ErrorDesc.addField(field, value)` assigns parsed XML text lists to descriptor attributes.
- `ErrorParser(filename)` parses XML with `xml.dom.minidom`, initializes `errors`, and calls `get_error_desc`.
- `getText(nodelist)` extracts lowercased text nodes.
- `handleErrorConf`, `handleError`, and `handleElement` traverse `<error>` entries and child tags.
- `get_error(opname, arg=None, env=None)` checks descriptors for a matching operation and returns a status code or mutates arguments.

## Control Flow
Initialization parses the XML document and builds one `ErrorDesc` per `<error>`. During proxy request handling, `get_error` scans descriptors in order. Nonmatching operations are skipped. For a match, it applies frequency by picking a random integer from `1..frequency` and only proceeding when it hits the upper bound. It sleeps for configured delay, then either chooses an error code from XML or chooses an error function. Numeric error strings are converted with `int`; symbolic names are matched against `nfsstat4`; functions are looked up on a fresh `Errors` object and called.

## State And Persistence Behavior
`ErrorParser` keeps the parsed DOM and an in-memory list of descriptors. It does not persist state. Randomness is global and seeded during parser construction. Delays block the proxy request-handling thread synchronously.

## Dependencies And Integration Points
The module depends on `xml.dom.minidom`, generated `nfsstat4`, logging, traceback/sys for error reporting, and `Errors` from `errorfunctions.py`. It is instantiated by `nfs4proxy.NFS4Proxy` and consulted for each operation while the request is still mutable.

## Risks And Edge Cases
- `__init__` calls `xml.dom.minidom.parse(filename)` before checking whether `filename is None`; passing no error file can fail before the intended "No error description" path.
- Symbolic error lookup uses `nfsstat4.iteritems()`, which is Python 2 style and breaks under Python 3.
- When a function injection is used, `get_error` returns `None` after mutation, so callers must rely on the mutated forwarded request.
- Exceptions during XML loading are swallowed after logging, leaving a partially initialized parser.
- Text is lowercased; symbolic constants are uppercased later, but function names and operation names must match expected lower-case conventions.
- Frequency defaults to one-in-ten, which may surprise tests expecting an error every time.

## Test Signals
Test signals include XML files with numeric and symbolic status codes, no-error descriptors, delay timing, deterministic behavior under seeded randomness, function mutation paths, and `None`/missing-file handling. Proxy-level tests should assert injected errors are encoded in the correct operation result and stop forwarding.
