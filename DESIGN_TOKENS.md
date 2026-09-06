# BEAZT Design System — Design Tokens

This document catalogs all CSS custom properties (design tokens) used in the BEAZT design system.

## Overview

The design system uses a three-layer token architecture:

1. **Primitive tokens** — Raw values (colors, sizes)
2. **Semantic tokens** — Purpose-based aliases
3. **Component tokens** — Component-specific values

All tokens are defined in `:root` in `static/css/style.css`.

---

## Foundation Colors

Background layers for depth hierarchy.

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-void` | `#030406` | Darkest background (page edges) |
| `--bg-base` | `#05070B` | Primary page background |
| `--bg-deep` | `#08101C` | Elevated sections |
| `--bg-elevated` | `#0C1625` | Cards, panels |
| `--bg-surface` | `#111D2E` | Interactive surfaces |
| `--bg-card` | `#0F1923` | Content cards |

---

## Accent Colors

Premium electric blue accent system.

| Token | Value | Usage |
|-------|-------|-------|
| `--accent-primary` | `#168BFF` | Primary interactive elements |
| `--accent-hover` | `#2590FF` | Hover state for primary |
| `--accent-muted` | `#0D6CD9` | Pressed/active state |
| `--accent-glow` | `rgba(22, 139, 255, 0.35)` | Standard glow effect |
| `--accent-glow-strong` | `rgba(22, 139, 255, 0.5)` | Strong glow effect |
| `--accent-glow-subtle` | `rgba(22, 139, 255, 0.15)` | Subtle glow effect |
| `--accent-soft` | `rgba(22, 139, 255, 0.12)` | Soft background tint |
| `--accent-line` | `rgba(22, 139, 255, 0.3)` | Accent border color |
| `--accent-deep` | `rgba(8, 48, 99, 0.5)` | Deep accent tint |

### Accent Gradients

| Token | Value |
|-------|-------|
| `--gradient-accent` | Blue gradient (primary buttons) |
| `--gradient-accent-soft` | Soft blue gradient (badges) |
| `--gradient-surface` | Surface elevation gradient |
| `--gradient-card` | Card background gradient |
| `--gradient-card-hover` | Card hover state gradient |
| `--gradient-hero` | Hero section ambient gradient |
| `--gradient-border-shine` | Border shine effect |

### Accent Ambient Effects

| Token | Value |
|-------|-------|
| `--ambient-blue-intense` | Intense blue radial glow |
| `--ambient-blue-soft` | Soft blue radial glow |
| `--ambient-blue-hero` | Hero-specific ambient glow |
| `--ambient-blue-cta` | CTA section ambient glow |
| `--ambient-glow-spot` | Central glow spot |

---

## Text Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--text-primary` | `#F0F4F8` | Headings, primary text |
| `--text-secondary` | `#A8B4C4` | Body text |
| `--text-muted` | `#6B7A8D` | Captions, labels |
| `--text-dim` | `#4A5568` | Disabled, hints |

---

## Status Colors

Semantic colors for state indication.

### Online/Success

| Token | Value | Usage |
|-------|-------|-------|
| `--status-online` | `#10B981` | Online indicator |
| `--status-online-bg` | `rgba(16, 185, 129, 0.12)` | Online background |
| `--status-online-border` | `rgba(16, 185, 129, 0.3)` | Online border |
| `--status-online-glow` | `rgba(16, 185, 129, 0.4)` | Online glow |

### Warning

| Token | Value | Usage |
|-------|-------|-------|
| `--status-warning` | `#F59E0B` | Warning indicator |
| `--status-warning-bg` | `rgba(245, 158, 11, 0.12)` | Warning background |
| `--status-warning-border` | `rgba(245, 158, 11, 0.3)` | Warning border |
| `--status-warning-glow` | `rgba(245, 158, 11, 0.4)` | Warning glow |

### Error/Danger

| Token | Value | Usage |
|-------|-------|-------|
| `--status-error` | `#EF4444` | Error indicator |
| `--status-error-bg` | `rgba(239, 68, 68, 0.12)` | Error background |
| `--status-error-border` | `rgba(239, 68, 68, 0.3)` | Error border |
| `--status-error-glow` | `rgba(239, 68, 68, 0.4)` | Error glow |

### Info

| Token | Value | Usage |
|-------|-------|-------|
| `--status-info` | `#3B82F6` | Info indicator |
| `--status-info-bg` | `rgba(59, 130, 246, 0.12)` | Info background |
| `--status-info-border` | `rgba(59, 130, 246, 0.3)` | Info border |

---

## Border Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--border-subtle` | `rgba(255, 255, 255, 0.06)` | Subtle separation |
| `--border-default` | `rgba(255, 255, 255, 0.1)` | Standard borders |
| `--border-strong` | `rgba(255, 255, 255, 0.18)` | Strong emphasis |
| `--border-accent` | `rgba(22, 139, 255, 0.4)` | Accent highlight |
| `--border-accent-subtle` | `rgba(22, 139, 255, 0.2)` | Subtle accent |

---

## Shadow Tokens

Depth levels for elevation.

| Token | Usage |
|-------|-------|
| `--shadow-xs` | Minimal elevation |
| `--shadow-sm` | Small elements |
| `--shadow-md` | Default cards |
| `--shadow-lg` | Large cards, modals |
| `--shadow-xl` | Floating elements |
| `--shadow-2xl` | Overlays, dropdowns |

---

## Glow Effect Tokens

Pre-defined glow effects for accent elements.

| Token | Usage |
|-------|-------|
| `--glow-accent` | Standard accent glow |
| `--glow-accent-strong` | Emphasized accent glow |
| `--glow-accent-subtle` | Subtle accent glow |
| `--glow-accent-card` | Card accent glow |
| `--glow-button` | Primary button glow |
| `--glow-button-hover` | Button hover glow |
| `--glow-inset` | Inset glow effect |
| `--glow-status-online` | Online status glow |
| `--glow-status-warning` | Warning status glow |
| `--glow-status-error` | Error status glow |

---

## Typography Tokens

### Font Families

| Token | Value | Usage |
|-------|-------|-------|
| `--font-display` | `"Inter", "Sora", system-ui, sans-serif` | Headings |
| `--font-body` | `"Inter", system-ui, -apple-system, sans-serif` | Body text |
| `--font-mono` | `"JetBrains Mono", "Fira Code", monospace` | Code, keys |

### Font Sizes

| Token | Value | Rem | Usage |
|-------|-------|-----|-------|
| `--text-xs` | `0.75rem` | 12px | Captions, badges |
| `--text-sm` | `0.875rem` | 14px | Small text |
| `--text-base` | `1rem` | 16px | Body text |
| `--text-lg` | `1.125rem` | 18px | Large body |
| `--text-xl` | `1.25rem` | 20px | Small headings |
| `--text-2xl` | `1.5rem` | 24px | Section headings |
| `--text-3xl` | `1.875rem` | 30px | Page headings |
| `--text-4xl` | `2.25rem` | 36px | Hero subheadings |

### Line Heights

| Token | Value | Usage |
|-------|-------|-------|
| `--leading-none` | `1` | Headings |
| `--leading-tight` | `1.25` | Navigation |
| `--leading-snug` | `1.375` | Card titles |
| `--leading-normal` | `1.5` | Default body |
| `--leading-relaxed` | `1.625` | Long-form text |
| `--leading-loose` | `2` | Legal/terms |

### Font Weights

| Token | Value | Usage |
|-------|-------|-------|
| `--font-normal` | `400` | Regular text |
| `--font-medium` | `500` | Emphasized |
| `--font-semibold` | `600` | Buttons, labels |
| `--font-bold` | `700` | Headings |
| `--font-extrabold` | `800` | Hero text |

---

## Spacing Tokens

4px base unit system.

| Token | Value | Pixels |
|-------|-------|--------|
| `--space-1` | `0.25rem` | 4px |
| `--space-2` | `0.5rem` | 8px |
| `--space-3` | `0.75rem` | 12px |
| `--space-4` | `1rem` | 16px |
| `--space-5` | `1.25rem` | 20px |
| `--space-6` | `1.5rem` | 24px |
| `--space-8` | `2rem` | 32px |
| `--space-10` | `2.5rem` | 40px |
| `--space-12` | `3rem` | 48px |
| `--space-16` | `4rem` | 64px |
| `--space-20` | `5rem` | 80px |
| `--space-24` | `6rem` | 96px |

---

## Border Radius Tokens

| Token | Value | Pixels | Usage |
|-------|-------|--------|-------|
| `--radius-xs` | `4px` | 4px | Small tags |
| `--radius-sm` | `6px` | 6px | Buttons, inputs |
| `--radius-md` | `10px` | 10px | Default cards |
| `--radius-lg` | `14px` | 14px | Large cards |
| `--radius-xl` | `20px` | 20px | Hero cards |
| `--radius-2xl` | `28px` | 28px | Premium cards |
| `--radius-full` | `9999px` | 9999px | Pills, badges |

---

## Transition Tokens

### Easing Curves

| Token | Value | Usage |
|-------|-------|-------|
| `--ease-out` | `cubic-bezier(0.22, 0.68, 0, 1.2)` | Reveal animations |
| `--ease-smooth` | `cubic-bezier(0.4, 0, 0.2, 1)` | Standard transitions |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Bouncy effects |

### Durations

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | `150ms` | Hover states |
| `--duration-normal` | `250ms` | Standard transitions |
| `--duration-slow` | `400ms` | Reveal animations |

---

## Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--z-base` | `0` | Default stacking |
| `--z-elevated` | `10` | Slight elevation |
| `--z-sticky` | `100` | Sticky elements |
| `--z-modal` | `500` | Modals, dialogs |
| `--z-toast` | `600` | Toast notifications |

---

## Interactive State Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--opacity-disabled` | `0.5` | Disabled state opacity |
| `--opacity-muted` | `0.6` | Muted element opacity |
| `--ring-width` | `2px` | Focus ring width |
| `--ring-offset` | `2px` | Focus ring offset |
| `--ring-color` | `var(--accent-primary)` | Focus ring color |
| `--focus-ring` | `0 0 0 2px var(--bg-base), 0 0 0 4px var(--accent-primary)` | Keyboard focus state |

---

## Component Tokens

### Button Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--button-padding-x` | `var(--space-4)` | Horizontal padding |
| `--button-padding-y` | `var(--space-3)` | Vertical padding |
| `--button-padding-x-sm` | `var(--space-3)` | Small variant padding |
| `--button-padding-y-sm` | `var(--space-2)` | Small variant padding |
| `--button-padding-x-lg` | `var(--space-6)` | Large variant padding |
| `--button-padding-y-lg` | `var(--space-4)` | Large variant padding |
| `--button-radius` | `var(--radius-md)` | Border radius |
| `--button-font-size` | `var(--text-sm)` | Font size |
| `--button-font-weight` | `var(--font-semibold)` | Font weight |
| `--button-min-height` | `44px` | Minimum touch target |
| `--button-min-width` | `44px` | Minimum width |

### Input Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--input-padding-x` | `var(--space-4)` | Horizontal padding |
| `--input-padding-y` | `var(--space-3)` | Vertical padding |
| `--input-radius` | `var(--radius-md)` | Border radius |
| `--input-font-size` | `var(--text-base)` | Font size |
| `--input-min-height` | `44px` | Minimum touch target |
| `--input-border` | `var(--border-default)` | Default border |
| `--input-focus-border` | `var(--accent-primary)` | Focus border color |
| `--input-focus-ring` | `var(--accent-glow-subtle)` | Focus ring |

### Card Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--card-padding` | `var(--space-6)` | Standard padding |
| `--card-padding-sm` | `var(--space-4)` | Compact padding |
| `--card-radius` | `var(--radius-lg)` | Border radius |
| `--card-border` | `var(--border-subtle)` | Default border |
| `--card-bg` | `var(--bg-card)` | Background color |

### Badge Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--badge-padding-x` | `var(--space-3)` | Horizontal padding |
| `--badge-padding-y` | `var(--space-1)` | Vertical padding |
| `--badge-radius` | `var(--radius-full)` | Border radius |
| `--badge-font-size` | `var(--text-xs)` | Font size |
| `--badge-font-weight` | `var(--font-bold)` | Font weight |

---

## Layout Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--container-max` | `1280px` | Standard container |
| `--container-sm` | `960px` | Narrow container |
| `--container-lg` | `1440px` | Wide container |
| `--container-padding` | `var(--space-6)` | Container side padding |

---

## Breakpoint Tokens (Reference)

For use in `@media` queries.

| Token | Value | Viewport |
|-------|-------|----------|
| `--breakpoint-sm` | `480px` | Large phones |
| `--breakpoint-md` | `768px` | Tablets |
| `--breakpoint-lg` | `1024px` | Small laptops |
| `--breakpoint-xl` | `1280px` | Desktops |
| `--breakpoint-2xl` | `1536px` | Large screens |

---

## Usage Examples

### Button Component

```css
.btn {
  padding: var(--button-padding-y) var(--button-padding-x);
  min-height: var(--button-min-height);
  font-size: var(--button-font-size);
  font-weight: var(--button-font-weight);
  border-radius: var(--button-radius);
  transition: all var(--duration-fast) var(--ease-smooth);
}

.btn-primary {
  background: var(--gradient-accent);
  color: #fff;
  box-shadow: var(--glow-button);
}

.btn-primary:hover {
  background: var(--accent-hover);
  box-shadow: var(--glow-button-hover);
  transform: translateY(-2px);
}
```

### Card Component

```css
.card {
  background: var(--gradient-card);
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  box-shadow: var(--shadow-md);
  transition: all var(--duration-normal) var(--ease-smooth);
}

.card:hover {
  border-color: var(--border-accent);
  box-shadow: var(--shadow-lg);
}
```

### Form Input

```css
.form-input {
  width: 100%;
  padding: var(--input-padding-y) var(--input-padding-x);
  min-height: var(--input-min-height);
  background: var(--bg-deep);
  border: 1px solid var(--input-border);
  border-radius: var(--input-radius);
  color: var(--text-primary);
  font-size: var(--input-font-size);
  transition: all var(--duration-fast) var(--ease-smooth);
}

.form-input:focus {
  outline: none;
  border-color: var(--input-focus-border);
  box-shadow: 0 0 0 4px var(--input-focus-ring);
}
```

### Status Badge

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--badge-padding-y) var(--badge-padding-x);
  font-size: var(--badge-font-size);
  font-weight: var(--badge-font-weight);
  border-radius: var(--badge-radius);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-success {
  background: var(--status-online-bg);
  color: var(--status-online);
  border: 1px solid var(--status-online-border);
  box-shadow: var(--glow-status-online);
}
```

---

## Maintenance Notes

1. **Color consistency**: All accent colors use `#168BFF` as the base. Adjust `--accent-primary` to shift the entire accent system.

2. **Spacing system**: The 4px base unit ensures consistent rhythm. Don't use arbitrary values outside this scale.

3. **Shadows**: The shadow scale provides clear elevation hierarchy. Use `--shadow-md` as the default for cards.

4. **Transitions**: The easing curves are tuned for the premium aesthetic. `--ease-smooth` is the safest choice for most interactions.

5. **Touch targets**: All interactive elements use `--button-min-height` (44px) to ensure accessibility on touch devices.
