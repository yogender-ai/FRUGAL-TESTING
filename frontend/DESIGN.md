---
name: AutomationPro Precision
colors:
  surface: '#fcf8ff'
  surface-dim: '#dcd8e3'
  surface-bright: '#fcf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f2fc'
  surface-container: '#f0ecf6'
  surface-container-high: '#eae6f1'
  surface-container-highest: '#e4e1eb'
  on-surface: '#1b1b22'
  on-surface-variant: '#464553'
  inverse-surface: '#303037'
  inverse-on-surface: '#f3eff9'
  outline: '#777584'
  outline-variant: '#c8c4d5'
  surface-tint: '#544fc0'
  primary: '#0d0060'
  on-primary: '#ffffff'
  primary-container: '#1f108e'
  on-primary-container: '#8b87fb'
  inverse-primary: '#c3c0ff'
  secondary: '#505f76'
  on-secondary: '#ffffff'
  secondary-container: '#d4e3ff'
  on-secondary-container: '#56657c'
  tertiary: '#300d00'
  on-tertiary: '#ffffff'
  tertiary-container: '#511c00'
  on-tertiary-container: '#d0805a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3b35a7'
  secondary-fixed: '#d4e3ff'
  secondary-fixed-dim: '#b8c7e2'
  on-secondary-fixed: '#0c1c30'
  on-secondary-fixed-variant: '#39485e'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb695'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#733515'
  background: '#fcf8ff'
  on-background: '#1b1b22'
  surface-variant: '#e4e1eb'
  terminal-bg: '#1e293b'
  terminal-header: '#0f172a'
  success-green: '#10b981'
  warning-amber: '#fbbf24'
  error-rose: '#f43f5e'
  surface-muted: '#f0ecf6'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md-mobile:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 12px
    letterSpacing: 0.05em
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
  gutter: 24px
  margin: 32px
  container-max: 1440px
---

## Brand & Style
The brand identity is rooted in **Engineering Precision** and **Operational Transparency**. It is designed for QA engineers and DevOps professionals who require high-density information without cognitive overload.

The visual style is a hybrid of **Corporate Modern** and **Technical Industrial**. It utilizes a systematic, utility-first approach with high-contrast functional areas (like the terminal-style log) to distinguish between human-readable configuration and machine-generated telemetry. The aesthetic should evoke feelings of speed, reliability, and "under-the-hood" control.

## Colors
The palette is dominated by a deep "Indigo Command" primary color, representing stability and authority. 

- **Primary & Secondary:** Used for navigational anchors and primary actions.
- **Functional Semantics:** The system relies heavily on a specialized "Terminal Palette" (dark slates and emeralds) for execution data, contrasting sharply against the light "Surface" palette of the configuration and management layers.
- **State Feedback:** Success, Warning, and Error states use high-vibrancy tints to ensure critical telemetry is immediately scannable.

## Typography
The system uses **Inter** for all UI-related tasks to maintain a neutral, systematic appearance. A strict hierarchy is established through weight variation rather than just size.

- **Data Density:** `body-md` and `body-sm` are the workhorses of the interface, optimized for readability in densley packed layouts.
- **Labels:** Uppercase `label-caps` are used exclusively for metadata and field descriptors to provide visual separation from user data.
- **Technical Context:** **JetBrains Mono** is reserved for logs, code snippets, and execution telemetry, signaling a shift in context from "Management" to "Execution."

## Layout & Spacing
The layout follows a **Fixed-Fluid Hybrid** model. The sidebar is a fixed 260px wide, while the main content area expands to a maximum of 1440px.

- **Grid Strategy:** A 12-column grid system is used with 24px gutters.
- **Modular Blocks:** Content is organized into "Panels" or "Cards" that stack vertically with 32px (stack-lg) spacing.
- **Inner Spacing:** Elements within cards use a consistent 16px (stack-md) rhythm.
- **Responsive Behavior:** On mobile, the sidebar collapses into a hamburger menu, and 3-column grid components reflow into a single column.

## Elevation & Depth
Hierarchy is achieved through **Tonal Layering** and **Low-Contrast Outlines** rather than aggressive shadows.

- **Primary Surfaces:** Use `#ffffff` (lowest container) to stand out against the `#fcf8ff` background.
- **Interaction Layers:** Subtle `shadow-sm` is used for containers to suggest lift without breaking the clean, technical aesthetic.
- **Borders:** `1px` solid borders using `outline-variant` are the primary method of defining boundaries between different functional modules.
- **The "Glass" Exception:** While the UI is mostly flat, buttons and critical action cards may use `shadow-md` or `shadow-lg` to create a clear "Call to Action" layer.

## Shapes
The shape language is **Soft-Square**. To maintain a professional, industrial feel, corner radii are kept disciplined:

- **Standard Elements:** 4px (0.25rem) for inputs and standard buttons.
- **Containers:** 8px (0.5rem) for main dashboard cards and the terminal execution panel.
- **Interactive Badges:** Full-radius (pill) shapes are used for checkboxes and status chips to distinguish them from structural elements.

## Components
- **Buttons:** Primary buttons are high-contrast indigo with bold text. Secondary buttons use fixed-tonal variants (lighter background, darker text). All buttons utilize a subtle `scale-95` transform on active states to provide tactile feedback.
- **Inputs:** Text fields feature a 1px border that transitions to a 2px indigo ring on focus. They always include an icon prefix for quick visual categorization.
- **Chips/Checkboxes:** Wrapped in a pill-shaped border with a hover state that fills the background with a subtle muted tint.
- **Terminal Panel:** A custom component with a dark slate background, emerald-tinted timestamps, and a pulsing "LIVE" indicator to represent active processes.
- **Status Badges:** Use a combination of a colored background and a filled icon (e.g., `verified_user`) to communicate state clearly across all accessibility needs.