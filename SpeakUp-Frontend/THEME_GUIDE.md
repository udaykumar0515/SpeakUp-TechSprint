# SpeakUp Theme Configuration Guide

This guide explains how to change the global color theme of the SpeakUp project based on a logo or brand identity without breaking the UI consistency.

## Core Principles
All colors are defined in `client/src/index.css` using HSL values (Hue Saturation% Lightness%). 
**Format**: `H S% L%` (e.g., `221 83% 53%`). Do not wrap in `hsl()`.

---

## 1. Primary Brand Color (Logo Color)
The primary color is the most impactful. Change these variables in `:root`:

- `--primary`: The main color from your logo.
- `--ring`: Usually matches `--primary`.
- `--primary-foreground`: Set to `210 40% 98%` (near white) for dark logos or `222 47% 11%` (near black) for very light logos.

## 2. Accent Color
Used for gradients and highlights to add depth.
- `--accent`: A complementary or secondary color from your logo.

## 3. Background & Surfaces
To keep the design clean, we use subtle off-whites for backgrounds.
- `--background`: Default is a very light blue-tinted white (`210 20% 98%`). 
- Change the first value (Hue) to match your primary color's hue for a subtle themed background.

---

## Quick Theme Recipes

### Modern Blue (Default)
```css
--primary: 221 83% 53%;
--accent: 262 83% 58%;
--ring: 221 83% 53%;
```

### Emerald Green (Professional & Growth)
```css
--primary: 142 71% 45%;
--accent: 160 84% 39%;
--ring: 142 71% 45%;
```

### Deep Purple (Creative & Elegant)
```css
--primary: 263 70% 50%;
--accent: 280 65% 60%;
--ring: 263 70% 50%;
```

### Vibrant Orange (Energetic)
```css
--primary: 24 95% 53%;
--accent: 45 93% 47%;
--ring: 24 95% 53%;
```

---

## Where to Change
1. Open `client/src/index.css`.
2. Locate the `:root` section.
3. Replace the HSL values for the variables mentioned above.
4. The Tailwind config in `tailwind.config.ts` will automatically pick up these changes using CSS variables.

## Important Notes
- **Contrast**: Always ensure the `foreground` variables (e.g., `--primary-foreground`) have high contrast against their background.
- **Consistency**: Avoid changing `--card`, `--muted`, or `--secondary` unless you want to change the "weight" of the UI panels. 
- **Dark Mode**: Currently, the theme is optimized for Light Mode with high-contrast surfaces.
