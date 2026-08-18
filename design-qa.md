# Home scroll design QA

- Source visual truth: `C:/Users/recha/AppData/Local/Temp/codex-clipboard-b97a034b-f165-45de-b647-f6ff41b03e5e.png`
- Implementation screenshot: unavailable because the Codex in-app browser could not initialize its trusted runtime
- Target viewport: 375 × 812 CSS px
- Source pixels: 519 × 887, containing a 375 × 812 app viewport at 1× CSS scale
- Implementation pixels and density: unavailable
- State: home, top position with recent product cards reaching the fixed bottom navigation

## Full-view comparison evidence

The source screenshot shows the lower part of the recent-product cards obscured by the fixed 84px bottom navigation. The implementation now separates the home content into a `height: calc(100% - 84px)` scroll container while leaving the navigation outside that container.

## Focused-region comparison evidence

Blocked. A rendered post-fix screenshot of the recent-product cards and bottom navigation could not be captured because the in-app browser connection failed before navigation.

## Findings

- [P1] Post-fix visual evidence is missing.
  - Location: home screen recent products and bottom navigation.
  - Evidence: the source screenshot is available, but the implementation screenshot is unavailable.
  - Impact: scrolling behavior and final card clearance cannot be visually confirmed in this environment.
  - Fix: deploy or open the local app, scroll the home content to the bottom at 375 × 812, and capture the visible card bottoms above the fixed navigation.

## Required fidelity surfaces

- Fonts and typography: unchanged by this patch; post-fix capture pending.
- Spacing and layout rhythm: scroll container and 32px recent-section bottom padding added; capture pending.
- Colors and visual tokens: unchanged.
- Image quality and asset fidelity: unchanged.
- Copy and content: unchanged.

## Comparison history

1. Initial evidence: recent-product card content was hidden behind the bottom navigation.
2. Fix: introduced `.home-scroll` with an 84px navigation-height reservation and vertical scrolling.
3. Post-fix evidence: blocked by unavailable in-app browser capture.

## Implementation checklist

- Deploy commit and reload the home screen.
- Verify vertical scrolling at 375 × 812.
- Verify both card bottoms are visible before the navigation.
- Capture the result and update this report.

final result: blocked
