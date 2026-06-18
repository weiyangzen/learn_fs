# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/fax2modem.c

Parses Class 2 fax modem status responses and updates `Modem` state.

Key behavior:
- `initfaxmodem()` initializes fax mode and phase.
- `parameters()` parses comma-separated numeric response payloads after `:`.
- Handlers process `+FCON`, `+FTSI`, `+FDCS`, `+FCFR`, `+FPTS`, `+FET`, and `+FHNG`.
- Stores remote station id, negotiated page parameters, page result, end-of-page signal, and hangup cause.

Important implementation details:
- `fcon()` advances from phase A to phase B.
- `ftsi()` strips quoted modem station id text and stores it once.
- `fhng()` returns `Rhangup`, unlike most fax responses which return `Rcontinue`.

Risks and invariants:
- Parameter arrays are filled without explicit upper-bound checks against malformed long responses.
- Fax behavior depends on modem response syntax matching expected Class 2 strings.
