"""
╔══════════════════════════════════════════════════════════╗
║          DD-DORNIER-CALCULATION  v1.0                    ║
║                                                          ║            
╚══════════════════════════════════════════════════════════╝
Run:  python DD-DORNIER-CALCULATION.py
Requires: Python 3.8+ with tkinter (standard library)
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import re
import math
from datetime import datetime


# ─────────────────── Colour Palette ────────────────────
BG_DARK       = "#0D1B2A"   # deep navy background
BG_MID        = "#1B2A3D"   # panel background
BG_CARD       = "#1E3A5F"   # card / frame background
ACCENT_GOLD   = "#FFD700"   # gold heading
ACCENT_CYAN   = "#00E5FF"   # cyan label
ACCENT_GREEN  = "#39FF14"   # neon green result
ACCENT_ORANGE = "#FF7F00"   # orange highlight
ACCENT_PINK   = "#FF6EC7"   # pink accent
TEXT_WHITE    = "#FFFFFF"
TEXT_LIGHT    = "#B0C4DE"
BTN_CALC      = "#FF6B00"   # orange calculate button
BTN_RESET     = "#CC0055"   # pink reset button
BTN_REPORT    = "#006400"   # dark green report button
ENTRY_BG      = "#0A2540"
ENTRY_FG      = "#00E5FF"


# ─────────────────── Calculation Engine ────────────────
def parse_quality(quality_str: str):
    """
    Extract the 'Sorts' value (2nd number after X in  '... X Sorts')
    e.g. '54.0"-9.30 OZS/40" - 9 X 11' → sorts=11
         '54.0"-9.30 OZS/40" - 11 X 11' → sorts=11
    """
    m = re.search(r'\b(\d+)\s*[Xx]\s*(\d+)', quality_str)
    if m:
        return int(m.group(2))   # 2nd number = Sorts
    return None


def calc_sorting_pinion(sorts: int, sp_val: int) -> int:
    """((sorts * 4) - sp_val) * 10"""
    return ((sorts * 4) - sp_val) * 10


def run_calculations(quality, avg_rpm, loom_diff, ozs, width, sp_val):
    """
    All formulas from the Excel sheet.
    Returns dict of results.
    """
    # ── 8HRS_100% ──────────────────────────────────────
    hrs_100 = 8 * 60 * avg_rpm                         # =8*60*AVG_RPM

    # ── Sorting Pinion ─────────────────────────────────
    sorts = parse_quality(quality)
    if sorts is None:
        raise ValueError("Cannot extract Sorts from Quality string.\n"
                         "Expected format: ... NxM  (e.g.  9 X 11)")
    sorting_pinion = calc_sorting_pinion(sorts, sp_val)

    # ── EFF (Efficiency %) ─────────────────────────────
    # EFF = ((LOOM_DIFF * 1000) / 8HRS_100%) * 100
    eff = ((loom_diff * 1000) / hrs_100) * 100

    # ── GSM ───────────────────────────────────────────
    # GSM = OZS * 30.51
    gsm = ozs * 30.51

    # ── GM/METER ──────────────────────────────────────
    # GM_PER_METER = (GSM * WIDTH) / 39.37
    gm_per_meter = (gsm * width) / 39.37

    # ── METER (Production Meters) ──────────────────────
    # METER = (8HRS_100% * (EFF/100)) / SORTING_PINION
    meter = (hrs_100 * (eff / 100)) / sorting_pinion

    # ── KG/LOOM ───────────────────────────────────────
    # KG_LOOM = METER * (GM_PER_METER / 1000)
    kg_loom = meter * (gm_per_meter / 1000)

    # ── OZS/YDS ───────────────────────────────────────
    # OZS_YDS = (OZS / 40) * WIDTH
    ozs_yds = (ozs / 40) * width

    return {
        "8HRS_100%":    hrs_100,
        "SORTS":        sorts,
        "SORTING_PINION": sorting_pinion,
        "EFF":          eff,
        "GSM":          gsm,
        "GM/METER":     gm_per_meter,
        "METER":        meter,
        "KG/LOOM":      kg_loom,
        "OZS/YDS":      ozs_yds,
    }


# ─────────────────── Main App ──────────────────────────
class DornierApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DD-DORNIER-CALCULATION  v1.0  |")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.minsize(860, 680)

        # Custom fonts
        self.ft_title  = font.Font(family="Helvetica", size=18, weight="bold")
        self.ft_sub    = font.Font(family="Helvetica", size=10, weight="bold")
        self.ft_label  = font.Font(family="Helvetica", size=10)
        self.ft_entry  = font.Font(family="Consolas",  size=11)
        self.ft_result = font.Font(family="Consolas",  size=12, weight="bold")
        self.ft_tiny   = font.Font(family="Helvetica", size=8)

        self.results = {}
        self._build_ui()

    # ── UI Builder ──────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_input_section()
        self._build_button_bar()
        self._build_result_section()
        self._build_status_bar()

    # ── Header ──────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg="#0A1628", pady=12)
        hdr.pack(fill=tk.X)

        tk.Label(hdr, text="⚙  DD-DORNIER-CALCULATION",
                 font=self.ft_title, bg="#0A1628", fg=ACCENT_GOLD
                 ).pack(side=tk.LEFT, padx=20)

        tk.Label(hdr, text="Dornier Loom Production Calculator  |  by Sukhen Nath",
                 font=self.ft_sub, bg="#0A1628", fg=TEXT_LIGHT
                 ).pack(side=tk.LEFT, padx=6)

        # live clock
        self.clock_var = tk.StringVar()
        tk.Label(hdr, textvariable=self.clock_var,
                 font=self.ft_sub, bg="#0A1628", fg=ACCENT_CYAN
                 ).pack(side=tk.RIGHT, padx=20)
        self._tick()

        # divider
        tk.Frame(self, bg=ACCENT_GOLD, height=2).pack(fill=tk.X)

    def _tick(self):
        self.clock_var.set(datetime.now().strftime("🕐  %d-%b-%Y   %H:%M:%S"))
        self.after(1000, self._tick)

    # ── Input Section ───────────────────────────────────
    def _build_input_section(self):
        outer = tk.Frame(self, bg=BG_DARK, pady=10)
        outer.pack(fill=tk.X, padx=20)

        tk.Label(outer, text="▌ INPUT PARAMETERS",
                 font=self.ft_sub, bg=BG_DARK, fg=ACCENT_ORANGE
                 ).pack(anchor=tk.W, pady=(0, 6))

        card = tk.Frame(outer, bg=BG_MID, bd=0, relief=tk.FLAT,
                        highlightbackground=ACCENT_CYAN,
                        highlightthickness=1)
        card.pack(fill=tk.X)

        # grid inside card
        inner = tk.Frame(card, bg=BG_MID, padx=16, pady=14)
        inner.pack(fill=tk.X)

        # ── Row 0: QUALITY (full width) ─────────────────
        self._lbl(inner, "QUALITY  (e.g.  54.0\"-9.30 OZS/40\" - 11 X 11)", 0, 0, span=6)
        self.var_quality = tk.StringVar(value='54.0"-9.30 OZS/40" - 11 X 11')
        e = tk.Entry(inner, textvariable=self.var_quality,
                     font=self.ft_entry, bg=ENTRY_BG, fg=ENTRY_FG,
                     insertbackground=ACCENT_GOLD, relief=tk.FLAT,
                     highlightbackground=ACCENT_CYAN, highlightthickness=1,
                     width=55)
        e.grid(row=1, column=0, columnspan=6, sticky=tk.W, pady=(0, 10))
        e.bind("<KeyRelease>", self._on_quality_change)

        # live sorts display
        self.sorts_var = tk.StringVar(value="Sorts = 11")
        tk.Label(inner, textvariable=self.sorts_var,
                 font=self.ft_sub, bg=BG_MID, fg=ACCENT_PINK
                 ).grid(row=1, column=6, sticky=tk.W, padx=10)

        # ── Row 1: numeric fields ───────────────────────
        fields_r1 = [
            ("AVG RPM",        "var_rpm",   "190"),
            ("LOOM DIFF / K-Picks", "var_loom_diff", "57"),
            ("OZS  (per 40\")", "var_ozs",  "9.3"),
        ]
        for col, (lbl, var, default) in enumerate(fields_r1):
            self._lbl(inner, lbl, 2, col * 2)
            sv = tk.StringVar(value=default)
            setattr(self, var, sv)
            e = tk.Entry(inner, textvariable=sv,
                         font=self.ft_entry, bg=ENTRY_BG, fg=ENTRY_FG,
                         insertbackground=ACCENT_GOLD, relief=tk.FLAT,
                         highlightbackground=ACCENT_CYAN, highlightthickness=1,
                         width=14)
            e.grid(row=3, column=col * 2, padx=(0, 20), pady=(0, 10), sticky=tk.W)

        # ── Row 2: WIDTH  +  SORTING PINION ────────────
        self._lbl(inner, "WIDTH  (inches)", 4, 0)
        self.var_width = tk.StringVar(value="54")
        tk.Entry(inner, textvariable=self.var_width,
                 font=self.ft_entry, bg=ENTRY_BG, fg=ENTRY_FG,
                 insertbackground=ACCENT_GOLD, relief=tk.FLAT,
                 highlightbackground=ACCENT_CYAN, highlightthickness=1,
                 width=14
                 ).grid(row=5, column=0, padx=(0, 20), pady=(0, 10), sticky=tk.W)

        self._lbl(inner, "SORTING PINION  (0–10)", 4, 2)
        self.var_sp = tk.IntVar(value=2)
        sp_frame = tk.Frame(inner, bg=BG_MID)
        sp_frame.grid(row=5, column=2, columnspan=4, sticky=tk.W)

        self.sp_combo = ttk.Combobox(
            sp_frame, textvariable=self.var_sp,
            values=list(range(11)), width=6,
            font=self.ft_entry, state="readonly"
        )
        self.sp_combo.pack(side=tk.LEFT)
        self.sp_combo.bind("<<ComboboxSelected>>", self._on_sp_change)

        # Sorting pinion formula display
        self.sp_formula_var = tk.StringVar()
        tk.Label(sp_frame, textvariable=self.sp_formula_var,
                 font=self.ft_sub, bg=BG_MID, fg=ACCENT_GREEN
                 ).pack(side=tk.LEFT, padx=14)

        inner.columnconfigure(1, minsize=30)
        inner.columnconfigure(3, minsize=30)
        inner.columnconfigure(5, minsize=30)

        self._on_quality_change()

    def _lbl(self, parent, text, row, col, span=1):
        tk.Label(parent, text=text,
                 font=self.ft_sub, bg=BG_MID, fg=ACCENT_CYAN
                 ).grid(row=row, column=col, columnspan=span, sticky=tk.W, pady=(6, 2))

    def _on_quality_change(self, event=None):
        sorts = parse_quality(self.var_quality.get())
        if sorts:
            self.sorts_var.set(f"✔  Sorts = {sorts}")
        else:
            self.sorts_var.set("⚠  Sorts not found")
        self._on_sp_change()

    def _on_sp_change(self, event=None):
        sorts = parse_quality(self.var_quality.get())
        sp_val = self.var_sp.get()
        if sorts:
            sp = calc_sorting_pinion(sorts, sp_val)
            self.sp_formula_var.set(
                f"(({sorts}×4)−{sp_val})×10  =  {sp}"
            )
        else:
            self.sp_formula_var.set("")

    # ── Button Bar ──────────────────────────────────────
    def _build_button_bar(self):
        bar = tk.Frame(self, bg=BG_DARK, pady=8)
        bar.pack(fill=tk.X, padx=20)

        btn_cfg = dict(font=self.ft_sub, relief=tk.FLAT, cursor="hand2",
                       padx=22, pady=8, bd=0)

        tk.Button(bar, text="⚡  CALCULATE",
                  bg=BTN_CALC, fg=TEXT_WHITE,
                  activebackground="#FF8C00", activeforeground=TEXT_WHITE,
                  command=self.calculate, **btn_cfg
                  ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(bar, text="↺  RESET",
                  bg=BTN_RESET, fg=TEXT_WHITE,
                  activebackground="#FF1493", activeforeground=TEXT_WHITE,
                  command=self.reset_fields, **btn_cfg
                  ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(bar, text="📋  FINAL REPORT",
                  bg=BTN_REPORT, fg=TEXT_WHITE,
                  activebackground="#228B22", activeforeground=TEXT_WHITE,
                  command=self.show_report, **btn_cfg
                  ).pack(side=tk.LEFT, padx=(0, 10))

    # ── Result Section ──────────────────────────────────
    def _build_result_section(self):
        outer = tk.Frame(self, bg=BG_DARK, pady=6)
        outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 8))

        tk.Label(outer, text="▌ CALCULATED RESULTS",
                 font=self.ft_sub, bg=BG_DARK, fg=ACCENT_ORANGE
                 ).pack(anchor=tk.W, pady=(0, 6))

        card = tk.Frame(outer, bg=BG_MID,
                        highlightbackground=ACCENT_GOLD,
                        highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(card, bg=BG_MID, padx=16, pady=14)
        inner.pack(fill=tk.BOTH, expand=True)

        # ── Top row: header boxes ───────────────────────
        headers = ["8HRS_100%", "SORTING\nPINION", "EFF %", "GSM",
                   "GM/METER", "METER", "KG/LOOM", "OZS/YDS"]
        colors  = [ACCENT_CYAN, ACCENT_PINK, ACCENT_GOLD, "#7FFF00",
                   ACCENT_ORANGE, "#00BFFF", ACCENT_GREEN, "#FF69B4"]

        self.res_vars = {}
        for col, (hdr, clr) in enumerate(zip(headers, colors)):
            box = tk.Frame(inner, bg=BG_CARD,
                           highlightbackground=clr, highlightthickness=2)
            box.grid(row=0, column=col, padx=5, pady=5, sticky=tk.NSEW)
            inner.columnconfigure(col, weight=1)

            tk.Label(box, text=hdr, font=self.ft_tiny,
                     bg=BG_CARD, fg=clr, wraplength=90
                     ).pack(pady=(8, 2))

            var = tk.StringVar(value="—")
            tk.Label(box, textvariable=var,
                     font=self.ft_result, bg=BG_CARD, fg=TEXT_WHITE,
                     wraplength=90
                     ).pack(pady=(2, 8))

            key = hdr.replace("\n", "")
            self.res_vars[key] = var

        # ── Sorting pinion explanation row ─────────────
        self.sp_explain_var = tk.StringVar(value="")
        tk.Label(inner, textvariable=self.sp_explain_var,
                 font=self.ft_sub, bg=BG_MID, fg=ACCENT_PINK
                 ).grid(row=1, column=0, columnspan=8,
                        sticky=tk.W, pady=(8, 2), padx=4)

        # ── Formula cheat-sheet ────────────────────────
        sep = tk.Frame(inner, bg=ACCENT_GOLD, height=1)
        sep.grid(row=2, column=0, columnspan=8, sticky=tk.EW, pady=8)

        formulas = (
            "Formulas:  "
            " 8HRS_100% = 8×60×RPM  │  "
            "EFF% = (LOOM_DIFF×1000 / 8HRS_100%)×100  │  "
            "GSM = OZS×30.51  │  "
            "GM/METER = GSM×WIDTH / 39.37  │  "
            "METER = 8HRS_100%×(EFF/100) / SORTING_PINION  │  "
            "KG/LOOM = METER×(GM_METER/1000)  │  "
            "OZS/YDS = (OZS/40)×WIDTH  │  "
            "SORTING_PINION = ((SORTS×4)−SP_VAL)×10"
        )
        tk.Label(inner, text=formulas, font=self.ft_tiny,
                 bg=BG_MID, fg=TEXT_LIGHT, wraplength=800, justify=tk.LEFT
                 ).grid(row=3, column=0, columnspan=8, sticky=tk.W, padx=4)

    # ── Status Bar ──────────────────────────────────────
    def _build_status_bar(self):
        tk.Frame(self, bg=ACCENT_GOLD, height=1).pack(fill=tk.X)
        self.status_var = tk.StringVar(value="Ready. Enter values and press ⚡ CALCULATE")
        tk.Label(self, textvariable=self.status_var,
                 font=self.ft_tiny, bg="#0A1628", fg=TEXT_LIGHT,
                 anchor=tk.W, pady=4
                 ).pack(fill=tk.X, padx=12)

    # ── Actions ─────────────────────────────────────────
    def calculate(self):
        try:
            quality  = self.var_quality.get().strip()
            avg_rpm  = float(self.var_rpm.get())
            loom_diff = float(self.var_loom_diff.get())
            ozs      = float(self.var_ozs.get())
            width    = float(self.var_width.get())
            sp_val   = int(self.var_sp.get())

            if not quality:
                raise ValueError("Quality field is empty.")
            if avg_rpm <= 0 or width <= 0 or ozs <= 0:
                raise ValueError("RPM, OZS and WIDTH must be positive.")

            self.results = run_calculations(quality, avg_rpm, loom_diff,
                                            ozs, width, sp_val)
            self.results["_inputs"] = {
                "QUALITY": quality,
                "AVG_RPM": avg_rpm,
                "LOOM_DIFF": loom_diff,
                "OZS": ozs,
                "WIDTH": width,
                "SP_VAL": sp_val,
            }

            # populate result boxes
            self.res_vars["8HRS_100%"].set(f"{self.results['8HRS_100%']:,.0f}")
            self.res_vars["SORTINGPINION"].set(f"{self.results['SORTING_PINION']:,}")
            self.res_vars["EFF%"].set(f"{self.results['EFF']:.2f}")
            self.res_vars["GSM"].set(f"{self.results['GSM']:.2f}")
            self.res_vars["GM/METER"].set(f"{self.results['GM/METER']:.2f}")
            self.res_vars["METER"].set(f"{self.results['METER']:.2f}")
            self.res_vars["KG/LOOM"].set(f"{self.results['KG/LOOM']:.2f}")
            self.res_vars["OZS/YDS"].set(f"{self.results['OZS/YDS']:.3f}")

            sorts  = self.results["SORTS"]
            sp     = self.results["SORTING_PINION"]
            self.sp_explain_var.set(
                f"  Sorting Pinion formula:  (({sorts} × 4) − {sp_val}) × 10  =  {sp}"
            )

            self.status_var.set(
                f"✔ Calculated successfully at {datetime.now().strftime('%H:%M:%S')}")

        except Exception as exc:
            messagebox.showerror("Input Error", str(exc))
            self.status_var.set(f"✘ Error: {exc}")

    def reset_fields(self):
        self.var_quality.set('54.0"-9.30 OZS/40" - 11 X 11')
        self.var_rpm.set("190")
        self.var_loom_diff.set("57")
        self.var_ozs.set("9.3")
        self.var_width.set("54")
        self.var_sp.set(2)
        for v in self.res_vars.values():
            v.set("—")
        self.sp_explain_var.set("")
        self.results = {}
        self._on_quality_change()
        self.status_var.set("Reset complete. Enter values and press ⚡ CALCULATE")

    def show_report(self):
        if not self.results:
            messagebox.showwarning("No Results",
                                   "Please press ⚡ CALCULATE first.")
            return

        r    = self.results
        inp  = r["_inputs"]
        now  = datetime.now().strftime("%d-%b-%Y  %H:%M:%S")

        win = tk.Toplevel(self)
        win.title("📋 DORNIER FINAL REPORT")
        win.configure(bg=BG_DARK)
        win.resizable(True, True)
        win.minsize(700, 580)

        # ── Report Header ────────────────────────────
        hdr = tk.Frame(win, bg="#0A1628", pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="╔══ DD-DORNIER-CALCULATION  ─  FINAL REPORT ══╗",
                 font=font.Font(family="Consolas", size=13, weight="bold"),
                 bg="#0A1628", fg=ACCENT_GOLD).pack()
        tk.Label(hdr, text=f"Generated : {now}",
                 font=font.Font(family="Consolas", size=9),
                 bg="#0A1628", fg=TEXT_LIGHT).pack()

        tk.Frame(win, bg=ACCENT_GOLD, height=2).pack(fill=tk.X)

        # ── Report Body ──────────────────────────────
        body = tk.Frame(win, bg=BG_DARK, padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        def row(parent, bg_row, label, value, lclr, vclr):
            f = tk.Frame(parent, bg=bg_row)
            f.pack(fill=tk.X, pady=1)
            tk.Label(f, text=label, width=22, anchor=tk.W,
                     font=font.Font(family="Consolas", size=11, weight="bold"),
                     bg=bg_row, fg=lclr).pack(side=tk.LEFT, padx=(4, 0))
            tk.Label(f, text=value, anchor=tk.W,
                     font=font.Font(family="Consolas", size=11),
                     bg=bg_row, fg=vclr).pack(side=tk.LEFT, padx=8)

        tk.Label(body, text="INPUT PARAMETERS",
                 font=font.Font(family="Helvetica", size=10, weight="bold"),
                 bg=BG_DARK, fg=ACCENT_ORANGE).pack(anchor=tk.W, pady=(0, 4))

        rows_in = [
            ("QUALITY",         inp["QUALITY"],      ACCENT_CYAN, TEXT_WHITE),
            ("AVG RPM",         f"{inp['AVG_RPM']:.0f}",       ACCENT_CYAN, TEXT_WHITE),
            ("8HRS_100%",       f"{r['8HRS_100%']:,.0f}",      ACCENT_CYAN, ACCENT_GREEN),
            ("LOOM DIFF",       f"{inp['LOOM_DIFF']:.0f}",     ACCENT_CYAN, TEXT_WHITE),
            ("OZS / 40\"",      f"{inp['OZS']}",               ACCENT_CYAN, TEXT_WHITE),
            ("WIDTH (inches)",  f"{inp['WIDTH']:.0f}\"",       ACCENT_CYAN, TEXT_WHITE),
            ("SORTING PINION",  f"{r['SORTING_PINION']}",      ACCENT_PINK, ACCENT_GREEN),
        ]
        for i, (lbl, val, lc, vc) in enumerate(rows_in):
            bg = BG_MID if i % 2 == 0 else BG_CARD
            row(body, bg, lbl, val, lc, vc)

        tk.Label(body, text="",  bg=BG_DARK).pack()
        tk.Label(body, text="CALCULATED RESULTS",
                 font=font.Font(family="Helvetica", size=10, weight="bold"),
                 bg=BG_DARK, fg=ACCENT_ORANGE).pack(anchor=tk.W, pady=(0, 4))

        rows_out = [
            ("EFF %",       f"{r['EFF']:.2f} %",         ACCENT_GOLD,   ACCENT_GREEN),
            ("GSM",         f"{r['GSM']:.2f}",            ACCENT_GOLD,   TEXT_WHITE),
            ("GM / METER",  f"{r['GM/METER']:.2f} g",    ACCENT_GOLD,   TEXT_WHITE),
            ("METER",       f"{r['METER']:.4f} m",        ACCENT_GOLD,   ACCENT_GREEN),
            ("KG / LOOM",   f"{r['KG/LOOM']:.4f} kg",    ACCENT_GOLD,   ACCENT_GREEN),
            ("OZS / YDS",   f"{r['OZS/YDS']:.3f}",       ACCENT_GOLD,   TEXT_WHITE),
        ]
        for i, (lbl, val, lc, vc) in enumerate(rows_out):
            bg = BG_MID if i % 2 == 0 else BG_CARD
            row(body, bg, lbl, val, lc, vc)

        # ── Sorting pinion breakdown ──────────────────
        sorts   = r["SORTS"]
        sp_val  = inp["SP_VAL"]
        sp_res  = r["SORTING_PINION"]
        tk.Label(body, text="",  bg=BG_DARK).pack()
        tk.Label(body,
                 text=f"  ⚙  Sorting Pinion Formula:  "
                      f"(({sorts}×4) − {sp_val}) × 10  =  {sp_res}",
                 font=font.Font(family="Consolas", size=11, weight="bold"),
                 bg=BG_DARK, fg=ACCENT_PINK).pack(anchor=tk.W)

        # ── Footer ───────────────────────────────────
        tk.Frame(win, bg=ACCENT_GOLD, height=2).pack(fill=tk.X)
        tk.Label(win, text="DD-DORNIER-CALCULATION  |  by Sukhen Nath",
                 font=font.Font(family="Helvetica", size=8),
                 bg="#0A1628", fg=TEXT_LIGHT, pady=5).pack(fill=tk.X)

        # close button
        tk.Button(win, text="✖  CLOSE",
                  bg=BTN_RESET, fg=TEXT_WHITE,
                  font=font.Font(family="Helvetica", size=9, weight="bold"),
                  relief=tk.FLAT, padx=14, pady=6, cursor="hand2",
                  command=win.destroy).pack(pady=8)


# ─────────────────── Style tweaks for ttk ──────────────
def apply_ttk_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TCombobox",
                    fieldbackground=ENTRY_BG,
                    background=ENTRY_BG,
                    foreground=ENTRY_FG,
                    selectbackground=ACCENT_GOLD,
                    selectforeground=BG_DARK,
                    arrowcolor=ACCENT_CYAN,
                    bordercolor=ACCENT_CYAN)
    style.map("TCombobox",
              fieldbackground=[("readonly", ENTRY_BG)],
              foreground=[("readonly", ENTRY_FG)])


# ─────────────────── Entry Point ───────────────────────
if __name__ == "__main__":
    app = DornierApp()
    apply_ttk_style()
    app.mainloop()