# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/cookies.c

This is the cookie engine embedded in `webfs`. It shares much of the standalone `webcookies.c` design but is wired directly into the webfs 9P `cookies` file and HTTP client.

Cookie/jar model:
- `Cookie` stores RFC-facing fields and internal deleted/mark/ondisk flags.
- `Jar` stores dynamic cookie array, qid, dirty bit, file, and lockfile.
- `%J` formats outgoing HTTP `Cookie:` headers.
- `%K` formats persistent/editable cookie lines.

Jar persistence:
- `readjar` constructs `L.<name>` lockfile path and calls `syncjar`.
- `syncjar` detects external file changes by qid, locks, merges disk cookies, deletes stale marked cookies, purges deleted slots, rewrites persistent non-session cookies, and updates qid.
- `closejar` expires and syncs on shutdown.

Cookie parsing/matching:
- Supports RFC2109-style and old Netscape-style Set-Cookie headers.
- `strtotime` parses GMT expiry formats.
- `parsehttp` scans raw response headers for `Set-Cookie:`.
- `parsecookie` parses cookie attributes, derives default domain/path, honors `expires`, `max-age`, and `secure`.
- `isbadcookie` implements path/domain security checks.
- `cookiesearch` returns sorted matching cookies for a request and honors `secure`.

9P integration:
- `cookieopen` syncs jar and creates an editable snapshot in fid aux state.
- `cookieread` returns that snapshot.
- `cookiewrite` edits the snapshot with a 16 MB cap.
- `cookieclunk` replaces jar contents according to edited text using mark/delete logic and syncs.
- `httpsetcookie` parses and stores response cookies.
- `httpcookies` syncs, searches, formats `%J`, closes the temporary subjar, and returns a heap string.

Notable behavior:
- `iscookiematch` treats `expire == 0` as non-expiring/matching, in addition to future expirations.
- `isdomainmatch` includes a compatibility case accepting `google.com` against `.google.com`, unlike the standalone `webcookies.c`.
- `httpcookies` calls `snprint("%J", j)` even when `cookiesearch` returns nil; `%J` emits an empty string for nil.
