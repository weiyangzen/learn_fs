# sources/test-tools/pynfs/nfs4.1/errorfunctions.py

## Purpose
`errorfunctions.py` contains mutation functions used by the proxy error-injection framework. Instead of returning a protocol status, these functions alter selected operation arguments to simulate malformed or surprising behavior.

## Important APIs, Types, And Functions
- `Errors.__init__()` seeds the random generator.
- `short_read(opname, arg, env=None)` reduces `arg.opread.count` to a random value in the original range.
- `wrong_offset(opname, arg, env=None)` attempts to move a READ offset to a random later offset.
- `wrong_sequenceid(opname, arg, env=None)` decrements a sequenceid field.

## Control Flow
`errorparser.ErrorParser.get_error` instantiates `Errors`, picks a named function from XML, and calls it with the operation name, mutable XDR argument object, and proxy compound environment. The function mutates the object in place; the proxy later repacks and forwards the modified request unless a status-code injection already returned.

## State And Persistence Behavior
The file stores no persistent state. It uses module-global random state and mutates the passed argument object directly for the lifetime of a proxied request.

## Dependencies And Integration Points
It depends only on `random`, but it is tightly coupled to generated XDR field names used by NFS READ and SEQUENCE-like operations. It integrates with `errorparser.py` and `nfs4proxy.py`.

## Risks And Edge Cases
- `wrong_offset` uses `arg.offset` and `arg.count`, while `short_read` uses `arg.opread.count`; if the generated wrapper stores fields under `opread`, `wrong_offset` will fail.
- `wrong_sequenceid` assumes a top-level `sa_sequenceid` field, which may not exist for all configured operations.
- There is no validation that the selected function matches the selected operation.
- Random mutation makes tests nondeterministic unless the random seed is controlled externally.

## Test Signals
Proxy tests should verify XML-selected functions are invoked, request XDR is mutated before forwarding, malformed field assumptions surface as logged proxy errors, and mutation frequency/delay from `errorparser` are honored around these functions.
