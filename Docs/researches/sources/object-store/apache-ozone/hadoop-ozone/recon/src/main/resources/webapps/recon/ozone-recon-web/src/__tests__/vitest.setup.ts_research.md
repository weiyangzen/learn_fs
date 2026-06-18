# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/vitest.setup.ts


Purpose: Global Vitest/jsdom setup for Recon web tests.

Important APIs/types/functions: Imports `@testing-library/jest-dom/vitest`, installs `window.localStorage`, `window.matchMedia`, and `Element.prototype.scrollIntoView` mocks.

Control flow/state/persistence: `localStorageMock` stores values in a closure with `getItem`, `setItem`, `removeItem`, and `clear`. Other browser APIs are replaced with `vi.fn()` shims.

Dependencies/integration points: Supports AntD, components using storage, and tests expecting jest-dom matchers.

Risks/test signals: Comment says jsdom lacks local storage, though modern jsdom often provides it; overriding may diverge from browser semantics. It mocks localStorage but not sessionStorage, even several tests/components use sessionStorage directly.
