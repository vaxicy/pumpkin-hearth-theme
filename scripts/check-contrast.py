# -*- coding: utf-8 -*-
"""WCAG contrast audit for the Pumpkin Hearth themes.

Every foreground/background pair VS Code actually draws is listed explicitly,
so a low-contrast color fails here instead of on someone's screen.

Usage:
    py -3 scripts/check-contrast.py          # report + fail on violations
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
VARIANTS = ["light", "dark"]

# (foreground, background, minimum ratio, what it paints)
UI_PAIRS = [
    ("foreground", "editor.background", 7.0, "editor text"),
    ("editor.foreground", "editor.background", 7.0, "editor text"),
    ("descriptionForeground", "editor.background", 4.5, "muted text"),
    ("input.placeholderForeground", "input.background", 4.5, "placeholder"),
    ("input.foreground", "input.background", 7.0, "input text"),
    ("dropdown.foreground", "dropdown.background", 7.0, "dropdown text"),
    ("quickInput.foreground", "quickInput.background", 7.0, "quick input"),
    ("editorWidget.foreground", "editorWidget.background", 7.0, "widget text"),
    ("editorHoverWidget.foreground", "editorHoverWidget.background", 7.0, "hover text"),
    ("editorSuggestWidget.foreground", "editorSuggestWidget.background", 7.0, "suggest text"),
    ("notifications.foreground", "notifications.background", 7.0, "notification"),
    ("titleBar.activeForeground", "titleBar.activeBackground", 4.5, "title bar"),
    ("titleBar.inactiveForeground", "titleBar.inactiveBackground", 3.5, "inactive title bar"),
    ("activityBar.foreground", "activityBar.background", 4.5, "activity bar icon"),
    ("activityBar.inactiveForeground", "activityBar.background", 3.0, "inactive icon"),
    ("sideBar.foreground", "sideBar.background", 5.0, "side bar text"),
    ("sideBarSectionHeader.foreground", "sideBarSectionHeader.background", 5.0, "section header"),
    ("statusBar.foreground", "statusBar.background", 5.0, "status bar"),
    ("statusBar.debuggingForeground", "statusBar.debuggingBackground", 4.5, "debug status"),
    ("statusBarItem.hoverBackground", "statusBar.background", 1.1, "status hover"),
    ("tab.activeForeground", "tab.activeBackground", 5.0, "active tab"),
    ("tab.inactiveForeground", "tab.inactiveBackground", 3.5, "inactive tab"),
    ("list.activeSelectionForeground", "list.activeSelectionBackground", 4.5, "list selection"),
    ("list.inactiveSelectionForeground", "list.inactiveSelectionBackground", 4.5, "list selection"),
    ("editorSuggestWidget.selectedForeground",
     "editorSuggestWidget.selectedBackground", 4.5, "suggest selection"),
    ("list.highlightForeground", "list.hoverBackground", 4.5, "list highlight"),
    ("list.focusHighlightForeground", "list.activeSelectionBackground", 4.5, "list focus"),
    ("button.foreground", "button.background", 4.5, "button"),
    ("button.secondaryForeground", "button.secondaryBackground", 4.5, "secondary button"),
    ("badge.foreground", "badge.background", 4.5, "badge"),
    ("activityBarBadge.foreground", "activityBarBadge.background", 4.5, "activity badge"),
    ("textLink.foreground", "editor.background", 4.5, "link"),
    ("textLink.activeForeground", "editor.background", 4.5, "active link"),
    ("editorLink.activeForeground", "editor.background", 4.5, "in-editor link"),
    ("terminal.foreground", "terminal.background", 7.0, "terminal text"),
    ("editorError.foreground", "editor.background", 4.5, "error"),
    ("editorWarning.foreground", "editor.background", 4.5, "warning"),
    ("editorInfo.foreground", "editor.background", 4.5, "info"),
    ("gitDecoration.addedResourceForeground", "editor.background", 4.5, "git added"),
    ("gitDecoration.modifiedResourceForeground", "editor.background", 4.5, "git modified"),
    ("gitDecoration.deletedResourceForeground", "editor.background", 4.5, "git deleted"),
    ("editorLineNumber.foreground", "editor.background", 3.0, "line numbers"),
    ("editorLineNumber.activeForeground", "editor.background", 4.5, "active line number"),
    ("editorCursor.foreground", "editor.background", 4.5, "cursor"),
    ("editorWhitespace.foreground", "editor.background", 1.4, "whitespace dots"),
    ("editorIndentGuide.activeBackground1", "editor.background", 1.35, "active indent guide"),
]

ANSI_MIN = 3.5
TOKEN_MIN = 4.5
COMMENT_MIN = 3.5
SEMANTIC_MIN = 4.5


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def channel_luminance(channel):
    c = channel / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (channel_luminance(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    a, b = luminance(hex_to_rgb(fg)), luminance(hex_to_rgb(bg))
    lo, hi = sorted((a, b))
    return (hi + 0.05) / (lo + 0.05)


def audit(variant):
    theme = json.loads(
        (BASE / "themes" / f"pumpkin-hearth-{variant}-color-theme.json").read_text(encoding="utf-8"))
    colors = theme["colors"]
    failures = []

    def check(fg, bg, minimum, label):
        missing = [k for k in (fg, bg) if k not in colors]
        if missing:
            failures.append((label, "missing " + ", ".join(missing), 0, minimum))
            return 0.0
        ratio = contrast(colors[fg], colors[bg])
        if ratio + 1e-9 < minimum:
            failures.append((label, f"{fg} {colors[fg]} on {bg} {colors[bg]}", ratio, minimum))
        return ratio

    ratios = []
    for fg, bg, minimum, label in UI_PAIRS:
        ratios.append((label, check(fg, bg, minimum, label)))

    for i in range(16):
        name = ("ansiBlack", "ansiRed", "ansiGreen", "ansiYellow", "ansiBlue", "ansiMagenta",
                "ansiCyan", "ansiWhite", "ansiBrightBlack", "ansiBrightRed", "ansiBrightGreen",
                "ansiBrightYellow", "ansiBrightBlue", "ansiBrightMagenta", "ansiBrightCyan",
                "ansiBrightWhite")[i]
        key = f"terminal.{name}"
        label = f"terminal {name}"
        ratios.append((label, check(key, "terminal.background", ANSI_MIN, label)))

    for rule in theme["tokenColors"]:
        fg = (rule.get("settings") or {}).get("foreground")
        if not fg:
            continue
        scope = ",".join(rule["scope"])
        minimum = COMMENT_MIN if "comment" in rule["scope"] else TOKEN_MIN
        label = f"token {scope}"
        ratio = contrast(fg, colors["editor.background"])
        if ratio + 1e-9 < minimum:
            failures.append((label, f"{fg} on editor.background {colors['editor.background']}",
                             ratio, minimum))
        ratios.append((label, ratio))

    for name, fg in theme.get("semanticTokenColors", {}).items():
        if not isinstance(fg, str) or not fg.startswith("#"):
            continue
        label = f"semantic {name}"
        ratio = contrast(fg, colors["editor.background"])
        if ratio + 1e-9 < SEMANTIC_MIN:
            failures.append((label, f"{fg} on editor.background {colors['editor.background']}",
                             ratio, SEMANTIC_MIN))
        ratios.append((label, ratio))

    print(f"\n== {variant} ==")
    for label, ratio in sorted(ratios, key=lambda item: item[1])[:8]:
        print(f"  lowest  {ratio:5.2f}  {label}")
    for label, detail, ratio, minimum in failures:
        print(f"  FAIL    {ratio:5.2f} < {minimum:.2f}  {label}: {detail}")
    print(f"  {len(ratios)} pairs checked, {len(failures)} failing")
    return failures


def main():
    failed = 0
    for variant in VARIANTS:
        failed += len(audit(variant))
    if failed:
        print(f"\n{failed} contrast violation(s)")
        return 1
    print("\nall contrast checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
