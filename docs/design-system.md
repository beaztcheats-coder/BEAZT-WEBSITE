# BEAZT Command · Design System

Source: ui-ux-pro-max / Retro-Futurism pattern — tuned for BEAZT’s neon ops aesthetic.

## Brand Pillars
- **Mood:** retro-futuristic command center, synth neon, polished cyber security cues.
- **Experience Goals:** instant clarity, low-latency feel, responsive chips/cards, minimal copy per block (< 12 words).
- **Avoid:** muted minimalism, emoji icons, copy blocks longer than two short sentences.

## Layout & Spacing
- 12-column desktop / 6-column tablet / stacked mobile grid.
- Spacing scale (px): 4, 8, 12, 16, 20, 28, 36, 48, 64.
- Containers: clamp(320px, 90vw, 1200px); hero bleeds may extend to 1440px.

## Color Tokens
| Token | Hex | Usage |
| --- | --- | --- |
| `--bg` | `#050414` | Body background, gradients.
| `--bg-alt` | `#0C0A1E` | Section contrast panels.
| `--surface` | `rgba(17,17,40,0.88)` | Card/terminal shells.
| `--surface-strong` | `rgba(8,8,28,0.95)` | Hero HUD, nav.
| `--grid-line` | `rgba(124, 58, 237, 0.35)` | Tech dividers.
| `--text` | `#F5F7FF` | Primary text.
| `--text-soft` | `#C5C8F9` | Body copy.
| `--text-muted` | `#9395D7` | Captions/labels.
| `--accent` | `#7C3AED` | Primary neon.
| `--accent-2` | `#36F0FF` | Cyan highlights.
| `--accent-hot` | `#F43F5E` | CTA, alerts.
| `--warning` | `#FFB347` | Status amber.
| `--success` | `#22F6A6` | Online chips.
| `--danger` | `#FF6B97` | Errors.

## Typography
- **Display:** Chakra Petch 700 — uppercase hero + nav labels.
- **Headline:** Space Grotesk 600.
- **Body:** Sora 400/500 (1.5–1.7 line height).
- **Numeric:** Space Grotesk 600 tabular (stats + pricing).
- Scale: 12 / 13 / 15 / 17 / 21 / 28 / 36 / 48 / 64.

## Iconography
- Lucide SVG set (inline or via `data-lucide`).
- Stroke 1.75px, rounded corners, 24px viewbox.
- Use `.icon` utility classes for consistent sizing + color.

## Motion
- Global transition token: 220–280ms cubic-bezier(0.22, 0.68, 0.27, 1).
- Hero: keep existing beast animation; add neon breathing + scanlines.
- Interactions: card hover tilt (rotateX/rotateY max 4deg), glow pulse for CTAs.
- Respect `prefers-reduced-motion` — disable ScrollReveal, hero loops, counters.

## Components
- **Nav:** glass bar, pill CTAs, sticky with subtle underglow.
- **Hero HUD:** stat chips, BEAZT stack info, < 3 words per label.
- **Pricing:** gradient cards with selection glow, inline savings chips, icon per plan duration.
- **Feature Grid:** 2-line headline, < 12-word blurb, neon icon badge.
- **FAQ:** accordion with chevron rotation + border glow, concise answers.

## Accessibility Checklist
- Contrast ≥ 4.5:1 for text; 3:1 for large icons.
- Hit areas ≥ 44px, `cursor: pointer`, focus rings with cyan outline.
- `prefers-reduced-motion` guard around hero, grid reveal, counters.
- Aria-labels on icon-only buttons, nav toggles, status chips.

## Copy Voice
- Active verbs, short commands ("Deploy Access", "Ping Support").
- Replace “build/Helios” with “BEAZT Stack".
- Mention delivery speed, uptime, private Discord; avoid filler sentences.
